# 06 — Беспроводная связь (LoRa / Meshtastic + Wi-Fi/BLE)

## Постановка вопроса

LoRa-модуль под стек Meshtastic (mesh-релеинг данных мониторинга) + Wi-Fi/BLE
для локальной конфигурации. Wi-Fi/BLE закрывается выбранным MCU (S3/S31 на кристалле,
P4 — через C6/C5 сопроцессор).

## Критерии выбора

1. Совместимость с Meshtastic firmware (официальный список плат/модулей).
2. Частотный план целевых регионов: EU868 / US915 (у Kickstarter-продукта — оба, SKU).
3. Выходная мощность: 22 dBm (EU limit +H flag), чувствительность.
4. Интерфейс SPI (занятость шин с Ethernet/W5500 — см. 01/05).
5. Цена и наличие.

## Варианты модулей

| Модуль | Чип | Мощность | Диапазоны | Цена (2026-10) | Комментарий |
|---|---|---|---|---|---|
| **EBYTE E22-900M22S** | SX1262 | 22 dBm | 850–930 МГц (один SKU на 868/915 с настройкой) | **$5.98** (ebyteiot) / LCSC C411293 | популярный выбор в самодельных Meshtastic-нодах; TCXO |
| EBYTE E22-400M22S | SX1262 | 22 dBm | 433–470 МГц | ~$6 | вариант 433 МГц (EU CN band) — не приоритет |
| Heltec HT-RA62 | SX1262 | 22 dBm | 868/915 | ~$7–9 | готовые Meshtastic-референсы |
| Semtech LR1121 | SX126x-class+ | 22 dBm | multiband + 2.4ГГц | ~$8–10 | избыточно, если нет нужды в 2.4ГГц LoRa |
| Adafruit RFM95W | SX1276 | 18 dBm (EU +14?) | 868/915 | ~$10 | старый чип, слабее RX |

- E22-900M22S: https://ebyteiot.com/products/sx1262-868mhz-module-electronic-components-22dbm-wireless-transceiver-lora-gfsk-iot-long-range-7km-ebyte-e22-900m22s-spi
- LCSC: https://www.lcsc.com/product-detail/C411293.html
- Meshtastic supported radios: https://meshtastic.org/docs/hardware/

## Аппаратные требования

- SPI + DIO1/NSS/BUSY/RST GPIO; TCXO питается от модуля (E22 — встроенный).
- SAW-фильтр + LNA (опционально) на 868 МГц; Antenna: SMA-разъём наружная
  (корпус 08 — вывести на верхнюю крышку).
- ESD-защита антеннного входа (см. опыт: USBLC6-2SC6 на наших платах).
- Разводка: 50Ω-микрополосок, keep-out под антенной.

## Firmware-требования

- Meshtastic: телеметрия узла (device/environment) — данные PM/газов в полях
  environment metrics или кастомный модуль (protobuf расширение).
- Проверить: официальный Meshtastic на выбранном MCU (S31 — под вопросом! если нет —
  радио-узел делается на отдельном дешёвом MCU? — архитектурное решение).
- Канал/ключи: конфигурация через BLE/Wi-Fi приложением Meshtastic.

## Открытые вопросы

1. **Meshtastic на ESP32-S31** — статус порта (если нет: P4/S3 путь или дочка-нода на C6?).
2. Один SKU для 868+915 (E22-900M22S покрывает оба) — упрощает Kickstarter-варианты.
3. Роль узла в mesh: router/client/repeater — влияет на duty-cycle и питание.

## Ссылки

- Meshtastic firmware repo: https://github.com/meshtastic/firmware
- E22-900M22S datasheet: https://www.ebyte.com/en/pdf-down.aspx?id=1567

*Цены проверены поиском 2026-10-06.*
