/*
 * Copyright (c) 2024 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file behaviors.h
 *  @brief FILL ME PLEASE!.
 */

#define ZMK_BEHAVIOR_OMIT(_name)                                                                   \
    !(defined(ZMK_BEHAVIORS_KEEP_##_name) ||                                                       \
      (defined(ZMK_BEHAVIORS_KEEP_ALL) && !defined(ZMK_BEHAVIORS_OMIT_##_name)))