# 05 — Ethernet PHY

## Постановка вопроса

Выбор PHY (физического приёмопередатчика) между MAC выбранного MCU и RJ45,
в зависимости от итогового MCU (см. `01-mcu/`).

## Критерии выбора

1. Интерфейс к MAC: RMII (10/100) или RGMII (1G) — по MCU.
2. Наличие референс-дизайнов в ESP-экосистеме (esp_eth драйвер).
3. Цена, доступность (2026–2027), корпус (QFN паяемость).
4. Auto-MDIX желательно.

## Варианты

| PHY | Интерфейс | Скорость | Цена (2026-10) | Где проверен |
|---|---|---|---|---|
| **IP101GRI** (IC Plus) | MII/RMII | 10/100 | ~$1–1.5 (LCSC C703537) | Olimex ESP32-POE, ESP32-P4 devkits, M5Stack PoESP32 |
| **LAN8720A** (Microchip) | RMII | 10/100 | ~$0.65–1.5 | десятки ESP32-плат; примечание: 25МГц кварц и разводка ref-clk критичны |
| **RTL8201F** (Realtek) | MII/RMII | 10/100 | ~$0.8–1.5 | много промышленных плат |
| **CH182D** (WCH) | RMII | 10/100 | ~$0.5–1 | свежие Waveshare P4-платы |
| **KSZ9131** (Microchip) | RGMII | 1G | ~$2.5–4 | если пойдёт путь ESP32-S31 GMAC (RGMII) |
| **W5500** (WIZnet) | SPI | 10/100 | $1.75–2.20 | ESP32-S3 путь (если выберут вариант A) |

- IP101GRI: https://www.lcsc.com/product-detail/Ethernet-Transceivers_IC-Plus-IP101GRI_C703537.html
- LAN8720A datasheet: https://ww1.microchip.com/downloads/aemDocuments/documents/UNG/ProductDocuments/DataSheets/LAN8720A-LAN8720Ai-Data-Sheet-DS00002165.pdf
- W5500: https://wiznet.io/products/ethernet-chips/w5500
- KSZ9131: https://www.microchip.com/en-us/product/KSZ9131

## Связка с выбором MCU

- **P4** → IP101GRI (дефолт ESP-IDF devkit) или CH182D/LAN8720.
- **S31** → RGMII PHY: KSZ9131 (или RTL8211F), если хотим гигабит; RMII-режим GMAC
  S31 позволяет и 10/100 PHY — уточнить по PRELIM-datasheet.
- **S3** → W5500 по SPI (это не PHY, а MAC+PHY+TCP/IP стек).

## Аппаратные требования

- Магнетика/RJ45: интегрированный разъём с трансформатором (напр. HanRun HR911105A / Pulse J1B1211CCD).
- PoE-пары подаются через центральные отводы трансформатора (стандартная схема) —
  согласовать с магнетикой, поддерживающей PoE (PoE-rated magnetics!).
- ESD-защита на TX/RX парах (напр. SP3010-04UTG) — уличная установка.

## Открытые вопросы

1. S31: подтвердить в актуальной редакции datasheet поддержку RMII-режима GMAC (для удешевления PHY).
2. Магнетика: выбрать RJ45 с PoE-отводами под выбранную PD-схему (04-power).

## Ссылки

- ESP-IDF Ethernet API (поддерживаемые PHY): https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_eth.html

*Цены проверены поиском 2026-10-06.*
