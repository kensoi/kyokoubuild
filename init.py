import importlib, engine, traceback

while True:
    importlib.reload(engine)
    bot = engine.CanaryBot('d7c3e40e8e9ab15257e03d54c002da4c44e87403725c4daa9ff1acd85a0b051d94042f776d2625f71aff6', "196752424")
    try:
        while bot.check():
            pass
    except:
        print(traceback.format_exc())