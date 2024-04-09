/*
 * Copyright (c) 2020 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

#include "generated/zmk/version.h"

struct fw_version get_fw_version(void) {
    return (struct fw_version){.zephyr = {.version.full = sys_kernel_version_get(),
                                          .repo =
                                              {
                                                  .branch = ZEPHYR_BRANCH,
                                                  .hash = ZEPHYR_HASH,
                                              }},
                               .zmk.repo = {
                                   .branch = ZMK_BRANCH,
                                   .hash = ZMK_HASH,
                               }};
}