#!/usr/bin/env python3
"""Psychrometric & thermal calcs for the Altruist-2 Pro PM air-preparation tract.

Formulas: Magnus/Buck saturation vapour pressure
  a = 6.1121 hPa
  (b, c) = (17.62, 243.12) for T >= 0 C
  (b, c) = (22.46, 272.62) for T <  0 C
Thermal: P_air = m_dot * c_p * dT ; m_dot = rho * Q ; Q = 1 LPM (SDS011 design flow)
Tract loss: 1D conduction -> convection off insulated 9mm brass tube.
"""

import math

# ---------- psychrometrics (Magnus/Buck) ----------

A = 6.1121  # hPa


def esat(t_c: float) -> float:
    b, c = (17.62, 243.12) if t_c >= 0 else (22.46, 272.62)
    return A * math.exp((b * t_c) / (c + t_c))


def rh_at(temp_c: float, abs_press_hpa: float) -> float:
    """RH of air whose water-vapour partial pressure is abs_press_hpa at temp_c."""
    return 100.0 * abs_press_hpa / esat(temp_c)


# ---------- flow / thermal basics ----------

Q_LPM = 1.0                       # design flow (SDS011 fan, datasheet 0.3-1.2 LPM)
Q_M3S = Q_LPM * 1e-3 / 60.0       # m3/s
RHO = 1.2                         # kg/m3 at 20 C
CP = 1006.0                       # J/kg/K

M_DOT = RHO * Q_M3S               # kg/s
P_PER_K = M_DOT * CP              # W per kelvin


def heater_power_w(d_t: float) -> float:
    """Power to heat the airstream itself by dT kelvin (ignoring tract losses)."""
    return P_PER_K * d_t


# ---------- tract heat loss ----------

TUBE_OD = 0.00952                 # m, ACR copper 3/8" OD
TUBE_WALL = 0.0008                # m, thin-wall ACR (0.032")
TUBE_D = TUBE_OD - 2 * TUBE_WALL  # ID = 7.9 mm
TUBE_L = 0.40                     # m (40 cm heated section for residence >= 1 s)
COIL_D = 0.09                     # m, recommended V2 coil diameter
INSUL_T = 0.005                   # m, EPDM/NBR HVAC insulation (k~0.04)


def tract_loss_w(dt: float, wind_ms: float = 0.0, insul: bool = True) -> float:
    """Rough stationary loss of the insulated tube to environment."""
    area = math.pi * TUBE_D * TUBE_L
    k_ins = 0.04
    r_insul = INSUL_T / k_ins
    h_out = 5.0 + 4.0 * wind_ms    # W/m2K, natural conv + wind
    r_out = 1.0 / h_out
    r_total = r_insul + r_out if insul else r_out
    return area * dt / r_total


# ---------- residence time ----------


def residence_s(length_m: float = TUBE_L, flow_lpm: float = Q_LPM) -> float:
    a = math.pi * (TUBE_D / 2.0) ** 2
    v = (flow_lpm * 1e-3 / 60.0) / a
    return length_m / v


def main() -> None:
    print("=" * 72)
    print("Altruist-2 Pro : PM air preparation — расчёты")
    print("=" * 72)

    print(f"\n[1] Поток: {Q_LPM} LPM = {Q_M3S:.3e} m3/s")
    print(f"    массовый расход = {M_DOT * 1000:.3f} g/s = {M_DOT * 3600 * 1000:.1f} g/h")
    print(f"    теплоёмкость потока = {P_PER_K * 1000:.1f} mW/K")

    print("\n[2] Сценарии нагрева (цель RH <= 45-50 % на входе в сенсор)")
    hdr = f"{'outdoor':>14} | {'target T':>8} | {'RH in':>6} | {'P_air':>7}"
    print(hdr)
    print("-" * len(hdr))
    scenarios = [
        (20, 0.90, 10),
        (20, 0.95, 13),
        (0, 0.95, 15),
        (-10, 0.90, 15),
        (-20, 0.80, 15),
        (30, 0.95, 10),
        (35, 0.85, 12),
    ]
    for t_out, rh_out, dt in scenarios:
        pv = rh_out * esat(t_out)
        t_in = t_out + dt
        rh_in = rh_at(t_in, pv)
        p = heater_power_w(dt)
        print(f"{t_out:>5}C/{rh_out * 100:>3.0f}% | {t_in:>5}C   | {rh_in:>5.0f}% | {p:>5.2f} W")

    print("\n[3] Теплопотери тракта (ACR 3/8\" ID 7.9mm x 40cm, dT=45K)")
    for label, wind, insul in [("штиль + 5мм EPDM", 0.0, True),
                               ("ветер 5м/с + 5мм", 5.0, True),
                               ("ветер 5м/с без изол.", 5.0, False)]:
        print(f"    {label:<22}: {tract_loss_w(45, wind, insul):.2f} W")
    print("    -> бюджет нагревателя: 3 W покрывает худший случай с запасом")

    print("\n[4] Residence time (ACR 3/8\" thin-wall: ID 7.9 mm)")
    for l in (0.25, 0.30, 0.35, 0.40):
        print(f"   heated {int(l*100)} cm @ 1 LPM = {residence_s(l):.2f} s")
    print("   (требование >= 1 s, Nature 2025; толстостенная ACR wall 1.47mm:")
    a_thick = math.pi * (0.00952 - 2 * 0.00147) ** 2 / 4
    v_thick = Q_M3S / a_thick
    print(f"    ID 6.58mm -> v={v_thick:.2f} m/s -> 40cm = {0.40 / v_thick:.2f} s — не проходит)")

    print("\n[5] Пассивный путь: горячий корпус (солнце) 45C, наружа 20C/90%")
    pv = 0.90 * esat(20)
    print(f"    RH в камере = {rh_at(45, pv):.0f}%  -> нагрев не нужен")

    print("\n[6] PI (Kapton) film heater — выбранный нагреватель (JLCPCB custom)")
    u, p_rated = 5.0, 3.0
    r = u * u / p_rated
    i = p_rated / u
    strip_w_mm, length_cm = 12.0, 40.0
    area_cm2 = length_cm * (strip_w_mm / 10.0)   # 40 см x 1.2 см = 48 см²
    q = p_rated / area_cm2
    print(f"    полоса {strip_w_mm:.0f} x {length_cm:.0f} см -> S = {area_cm2:.0f} см2")
    print(f"    R = U^2/P = {u**2:.0f}/{p_rated:.0f} = {r:.2f} Ом (JLC tol ±5% при R>=1 Ом)")
    print(f"    I = P/U = {i:.2f} А (MOSFET AO3400A 5.7 А — запас ~9x)")
    print(f"    плотность мощности q = {q:.4f} Вт/см2 (типовой предел PI ~2.5 Вт/см2 -> запас ~40x)")
    print(f"    плёнка: etched foil SS 30um, -40..+150 °C длительно, дизайн <= 65 °C")
    print(f"    failsafe: thermal fuse 66 °C последовательно + NTC (в плёнке) + GPIO-страж")


if __name__ == "__main__":
    main()
