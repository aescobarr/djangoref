import pandas as pd


def main():
    df1 = pd.read_excel(
        '/home/webuser/dev/django/djangoref/Book_1.xlsx',
        engine='openpyxl',
    )
    # print(df1)
    # print(df1.columns[0])

    # for col in df1.columns:
        # print(col)

    numpy = df1.to_numpy()

    for row in numpy:
        print(row)

    # print(numpy)

if __name__ == '__main__':
    main()
