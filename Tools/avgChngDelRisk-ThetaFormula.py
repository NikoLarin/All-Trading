import math

# Inputs
waoc = float(input("Enter the average weekly move (WAOC): "))
delta = float(input("Enter the delta of the option: "))
gamma = float(input("Enter the gamma of the option: "))
theta = float(input("Enter the theta of the option per day: ")) 
dte_calendar = int(input("Enter the total calendar days to expiration: "))

# Convert calendar days → approximate trading days (5 trading days per 7 days)
dte_trading = dte_calendar * (5/7)

# Daily move (assuming 5 trading days per week)
deltaSDaily = waoc / 5

# Daily risk
riskDaily = abs(delta) * deltaSDaily + 0.5 * gamma * (deltaSDaily ** 2)

# Multi-day risk
riskLinear = riskDaily * dte_trading
riskRMS = riskDaily * math.sqrt(dte_trading)

# Total Theta over full calendar DTE
thetaTotal = abs(theta) * dte_calendar

# --- Outputs ---
print("\n--- Daily Risk ---")
print(f"Daily risk: ${riskDaily:.2f}")
print(f"Daily Theta: ${abs(theta):.2f}")

if riskDaily > abs(theta):
    print("Decision (daily): DO NOT sell")
else:
    print("Decision (daily): OK to sell")

print("\n--- Multi-Day Risk ---")
print(f"Linear total risk (worst-case): ${riskLinear:.2f}")
print(f"RMS total risk (typical): ${riskRMS:.2f}")
print(f"Total Theta over {dte_calendar} calendar days: ${thetaTotal:.2f}")

# Multi-day decisions
if riskLinear > thetaTotal:
    print("Decision (linear / worst-case): DO NOT sell")
else:
    print("Decision (linear / worst-case): OK to sell")

if riskRMS > thetaTotal:
    print("Decision (RMS / typical): DO NOT sell")
else:
    print("Decision (RMS / typical): OK to sell")
