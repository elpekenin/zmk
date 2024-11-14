/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file matrix_transform.h
 *  @brief FILL ME PLEASE!.
 */

#define KT_ROW(item) (item >> 8)
#define KT_COL(item) (item & 0xFF)

#define RC(row, col) (((row) << 8) + (col))