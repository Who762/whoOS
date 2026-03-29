def set_power(on: bool):
    try:
        import smbus2
        bus = smbus2.SMBus(1)
        # 0x00 = command mode, 0xAF = display on, 0xAE = display off
        bus.write_i2c_block_data(0x3C, 0x00, [0xAF if on else 0xAE])
        bus.close()
        return True
    except Exception as e:
        return False
