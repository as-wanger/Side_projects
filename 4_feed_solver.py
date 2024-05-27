import xlwings as xw
import pandas as pd
import pulp


def func1():
    wb = xw.Book("example.xlsx")
    sheet1 = wb.sheets[1]
    content = sheet1["B2:U16"].value
    title = content.pop(0)

    # check input data
    df = pd.DataFrame(data=content, columns=title).fillna(0)

    # variables
    df = df.loc[:, ["項目", "價格", "CP", "ME", "Ca", "AP"]]

    # remove unit
    df = df.iloc[1:]

    df = df.set_index(df.columns[0])

    # add threshold
    kwargs = {'黃玉米': [0, 100, 'Continue'],
              '大豆粕': [0, 100, 'Continue'],
              '全脂豆粉': [0, 100, 'Continue'],
              '魚粉，鯡魚，大西洋': [0, 3, 'Continue'],
              '大豆油(植物油)': [0, 3, 'Continue'],
              '廢棄香菇菇包': [0, 100, 'Continue'],
              '磷酸一鈣': [0, 100, 'Continue'],
              '石灰石粉': [0, 100, 'Continue'],
              'DL-Met': [0.25, 0.25, 'Continue'],
              'L-Lys': [0.12, 0.12, 'Continue'],
              '食鹽': [0.3, 0.3, 'Continue'],
              'Vitamin': [0.1, 0.1, 'Continue'],
              'Mineral': [0.02, 0.02, 'Continue']
              }
    d = {}

    # minimum: '價格'
    MyProbLP = pulp.LpProblem("LPProbDemo1", sense=pulp.LpMinimize)

    for name in kwargs:
        d[name] = pulp.LpVariable(name, lowBound=kwargs[name][0], upBound=kwargs[name][1], cat=kwargs[name][2])

    MyProbLP += sum(v * df.loc[k]["價格"] for k, v in d.items()) / 100

    # restriction: ['100%'] + df.columns: ['CP', 'ME', 'Ca', 'AP']
    restriction = {"CP": 21.5, "ME": 3200, "Ca": 0.87, "AP": 0.435}

    MyProbLP += (sum(v for v in d.values()) == 100)
    MyProbLP += (sum(v * df.loc[k]["CP"] for k, v in d.items()) / 100 == restriction["CP"])
    MyProbLP += (sum(v * df.loc[k]["ME"] for k, v in d.items()) / 100 == restriction["ME"])
    MyProbLP += (sum(v * df.loc[k]["Ca"] for k, v in d.items()) / 100 == restriction["Ca"])
    MyProbLP += (sum(v * df.loc[k]["AP"] for k, v in d.items()) / 100 == restriction["AP"])

    MyProbLP.solve()
    print("Output status:", pulp.LpStatus[MyProbLP.status])

    # variable optimal
    for v in MyProbLP.variables():
        print(v.name, "=", v.varValue)

    print("Lowest Price(x) = ", pulp.value(MyProbLP.objective))


def pd_set(col, width, row):
    # 顯示最大列數
    pd.set_option('display.max_rows', col)
    # 橫數寬度
    pd.set_option('display.width', width)
    # 顯示最大行數
    pd.set_option('display.max_columns', row)


def main():
    pd_set(10, 400, 14)
    func1()


if __name__ == '__main__':
    main()
