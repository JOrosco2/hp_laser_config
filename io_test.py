import user_io.hp_laser_cli as cli

"""
Unit test script to test all user interface functions
"""

resp = cli.display_menu()
print(f"******************You entered {resp}******************")

info = cli.get_config_info()
print(f"******************Config Info******************")
print(info)