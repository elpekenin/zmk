/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file wpm_state_changed.h
 *  @brief FILL ME PLEASE!.
 */

#pragma once

#include <zephyr/kernel.h>
#include <zmk/event_manager.h>
#include <zmk/wpm.h>

struct zmk_wpm_state_changed {
    int state;
};

ZMK_EVENT_DECLARE(zmk_wpm_state_changed);
