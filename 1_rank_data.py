class Data:
    def __init__(self):
        self.stores = {}

    def add_store(self, company, rank):
        self.stores[company] = rank

    def show_stores(self):
        rank_1 = dict(sorted(self.stores.items(), key=lambda x: x[1], reverse=True))
        for i, (key, value) in enumerate(rank_1.items()):
            print(f"{key:<6}, {value:>4}, {i+1}/{len(self.stores)}")


def main():
    company = {"Shoppe": 1050,
               "ASUS": 100,
               "Google": 1000,
               "Amazon": 800,
               "Meta": 500}
    d = Data()
    for key, value in company.items():
        d.add_store(key, value)
    d.show_stores()


if __name__ == '__main__':
    main()