#include <stdio.h>
#include <stdbool.h>
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/irq.h"
#include "pico/time.h"

// -- LIDAR UART config --
#define LIDAR_UART         uart0
#define LIDAR_BAUD         115200
#define LIDAR_UART_TX_PIN  0   // not using this currently
#define LIDAR_UART_RX_PIN  1

// -- Buffer -- (simple ring buffer for bytes received in UART RX ISR)
#define BUFF_SIZE 512 
static volatile uint8_t  buff[BUFF_SIZE];
static volatile uint16_t buff_head = 0;
static volatile uint16_t buff_tail = 0;

static inline uint16_t buff_next(uint16_t i) { 
    i++;
    return (i >= BUFF_SIZE) ? 0 : i;
}

static inline bool buff_empty(void) {
    return buff_head == buff_tail;
}

static inline void buff_push(uint8_t byte) {
    uint16_t next_idx = buff_next(buff_head);
    if (next_idx == buff_tail) {
        // handle overflow by dropping oldest byte to keep stream moving
        buff_tail = buff_next(buff_tail);
    }
    buff[buff_head] = byte; // put new byte in buffer head
    buff_head = next_idx; // advance head
}

static inline bool buff_pop(uint8_t *out) {
    if (buff_empty()) return false;
    
    *out = buff[buff_tail]; // get byte from buffer tail
    buff_tail = buff_next(buff_tail); // advance tail
    return true;
}

// -- UART RX ISR --
static void lidar_uart_rx(void) {
    while (uart_is_readable(LIDAR_UART)) {
        buff_push((uint8_t)uart_getc(LIDAR_UART));
    }
}

// -- LIDAR frame parsing --
// TF-Luna LIDAR frame (9 bytes):
// 0: 0x59
// 1: 0x59
// 2: Dist_L
// 3: Dist_H
// 4: Strength_L
// 5: Strength_H
// 6: Temp_L
// 7: Temp_H
// 8: Checksum (low 8 bits of sum bytes 0..7) if used (ignoring currently)
typedef struct {
    uint16_t distance_cm;
    uint16_t strength;
    int16_t  temp_c_x100;      // approx: temp_raw/8 - 256
    absolute_time_t timestamp;
} lidar_frame_t;

static bool parse_lidar_frame(lidar_frame_t *out) {
    static uint8_t frame[9];
    static int idx = 0;

    uint8_t byte;
    while (buff_pop(&byte)) {
        // for index 0 and 1, we look for the 0x59 bytes
        if (idx == 0) {
            if (byte == 0x59) frame[idx++] = byte;
            continue;
        }
        if (idx == 1) {
            if (byte == 0x59) frame[idx++] = byte;
            else idx = 0;
            continue;
        }

        // for indexes 3 through 8, we just store the byte
        frame[idx++] = byte;

        if (idx == 9) {
            idx = 0; // reset idx for next frame

            // not using checksum

            // gather data from frame
            uint16_t dist = (uint16_t)frame[2] | ((uint16_t)frame[3] << 8);
            uint16_t str  = (uint16_t)frame[4] | ((uint16_t)frame[5] << 8);
            uint16_t temp_raw = (uint16_t)frame[6] | ((uint16_t)frame[7] << 8);

            // Convert temp to Celsius x100 for better precision without floats
            // temp(C) ≈ temp_raw / 8 - 256
            int16_t temp_c100 = (int16_t)(((int32_t)temp_raw * 100) / 8 - 25600);

            // put data in frame struct
            out->distance_cm = dist;
            out->strength = str;
            out->temp_c_x100 = temp_c100;
            out->timestamp = get_absolute_time();
            return true;
        }
    }
    return false;
}

int main() {
    stdio_init_all();

    // Init UART
    uart_init(LIDAR_UART, LIDAR_BAUD);
    gpio_set_function(LIDAR_UART_RX_PIN, GPIO_FUNC_UART);
    gpio_set_function(LIDAR_UART_TX_PIN, GPIO_FUNC_UART); // optional, ok to leave
    uart_set_format(LIDAR_UART, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(LIDAR_UART, true);

    // Setup IRQ
    int irq = (LIDAR_UART == uart0) ? UART0_IRQ : UART1_IRQ;
    irq_set_exclusive_handler(irq, lidar_uart_rx);
    irq_set_enabled(irq, true);
    uart_set_irq_enables(LIDAR_UART, true, false); // RX only

    // Print throttling: 20 Hz
    // necessary so there isn't a big backlog of prints
    const uint32_t print_period_us = 50 * 1000; // 50ms
    absolute_time_t next_print = get_absolute_time();

    lidar_frame_t frame = {0};
    uint32_t frames_total = 0;

    while (true) {
        bool got_frame = false;

        // Get available frames from buffer
        while (parse_lidar_frame(&frame)) {
            frames_total++;
            got_frame = true;
        }

        // Check if it is time to print (20 Hz to prevent backlog)
        if (absolute_time_diff_us(get_absolute_time(), next_print) <= 0) {
            // set next print time
            next_print = delayed_by_us(next_print, print_period_us);

            // Check if there is a frame to look at
            if (got_frame || frames_total > 0) {
                int16_t t = frame.temp_c_x100; // get temp in C x100
                int16_t t_abs = (t < 0) ? -t : t; // absolute value for printing

                printf("Distance: %u cm | Strength: %u | Temp: %d.%02d C | total=%lu\n",
                        frame.distance_cm,
                        frame.strength,
                        t / 100, t_abs % 100,
                        (unsigned long)frames_total);
            } else {
                printf("Waiting for TF-Luna frames...\n");
            }
        }

        tight_loop_contents();
    }
}