/*
 * Copyright (c) 2023 The ZMK Contributors
 *
 * SPDX-License-Identifier: MIT
 */

/** @file reset_settings_file.c
 *  @brief FILL ME PLEASE!.
 */

#include <zephyr/fs/fs.h>

#include <zmk/settings.h>

#include <zephyr/logging/log.h>
LOG_MODULE_DECLARE(zmk, CONFIG_ZMK_LOG_LEVEL);

int zmk_settings_erase(void) {
    LOG_INF("Erasing settings file");

    int rc = fs_unlink(CONFIG_SETTINGS_FS_FILE);
    if (rc) {
        LOG_ERR("Failed to unlink '%s': %d", CONFIG_SETTINGS_FS_FILE, rc);
    }

    return rc;
}
