from game import Game, GameConfig, GameDimensions, GameGui


def main():
    TPS = 60
    game_dimensions = GameDimensions(1200, 1200)
    config = GameConfig(game_dimensions, TPS)
    g = Game(config)

    gui = GameGui(g)
    gui.play()


if __name__ == "__main__":
    main()
