/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file activity_state_changed.h
 *  @brief FILL ME PLEASE!.
 */

#pragma once

#include <zephyr/kernel.h>
#include <zmk/event_manager.h>
#include <zmk/activity.h>

struct zmk_activity_state_changed {
    enum zmk_activity_state state;
};

ZMK_EVENT_DECLARE(zmk_activity_state_changed);