from ida4sims_cli.functions.LexisAuthManager import LexisAuthManager

lexisAuthManager = LexisAuthManager()


def main():
    lexisAuthManager.logout()
    print("Successfully logged out")

if __name__ == "__main__":
    main()