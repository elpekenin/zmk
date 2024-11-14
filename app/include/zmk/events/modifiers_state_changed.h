/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file modifiers_state_changed.h
 *  @brief FILL ME PLEASE!.
 */

#pragma once

#include <zephyr/kernel.h>
#include <zmk/keys.h>
#include <zmk/event_manager.h>

struct zmk_modifiers_state_changed {
    zmk_mod_flags_t modifiers;
    bool state;
};

ZMK_EVENT_DECLARE(zmk_modifiers_state_changed);