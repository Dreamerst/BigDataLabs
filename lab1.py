import pandas
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import seaborn as sns


sql = """
    SELECT
      ra."year" AS race_year,
      ra."date"::date AS race_date,
      c.country AS circuit_country,
      c."lat" AS circuit_lat,
      c."lng" AS circuit_lng,
      d."driverid" AS driver_id,
      r."positionorder"::integer AS position_order,
      r."points"::numeric AS points
    FROM "results" r
    JOIN "races"   ra ON r."raceid"    = ra."raceid"
    JOIN "drivers" d  ON r."driverid"  = d."driverid"
    JOIN "circuits" c ON ra."circuitid" = c."circuitid"
    ;
    """


def connect():
    connection_string = "postgresql://postgres:1234@localhost:5432/postgres"
    engine = create_engine(connection_string)

    df = pandas.read_sql(sql, engine)

    engine.dispose()
    return df


def create_histograms(df):
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    axes[0].hist(df['position_order'], bins=20, edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Позиция финиша')
    axes[0].set_ylabel('Частота')
    axes[0].set_title('Распределение позиций финиша гонщиков')
    axes[0].grid(True, alpha=0.3)

    axes[1].hist(df['points'], bins=30, edgecolor='black', alpha=0.7, color='orange')
    axes[1].set_xlabel('Количество очков')
    axes[1].set_ylabel('Частота')
    axes[1].set_title('Распределение заработанных очков')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def create_plots(df):
    plt.figure(figsize=(14, 6))

    years_to_plot = sorted(df['race_year'].unique())[::10]
    df_filtered = df[df['race_year'].isin(years_to_plot)]

    heatmap_data = df_filtered[df_filtered['position_order'] <= 10].pivot_table(
        values='points',
        index='position_order',
        columns='race_year',
        aggfunc='mean'
    )
    plt.subplot(1, 2, 1)
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='.1f', linewidths=0.5)
    plt.title('Средние очки по годам и позициям')
    plt.xlabel('Год')
    plt.ylabel('Позиция финиша')
    plt.tight_layout()

    plt.subplot(1, 2, 2)

    scatter = plt.scatter(
        x=df['circuit_lng'],
        y=df['circuit_lat'],
        c=df['race_year'],
        s=df['points'] * 10,
        alpha=0.6,
        cmap='viridis'
    )

    plt.colorbar(scatter, label='Год проведения гонки')
    plt.xlabel('Долгота')
    plt.ylabel('Широта')
    plt.title('Расположение трасс с учетом года и очков')

    sizes = [10, 50, 100, 250]
    labels = ['1 очко', '5 очков', '10 очков', '25 очков']

    for size, label in zip(sizes, labels):
        plt.scatter([], [], s=size, c='gray', alpha=0.6, label=label)

    plt.legend(title='Количество очков', loc='upper right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main():
    df = connect()
    create_histograms(df)
    create_plots(df)


if __name__ == "__main__":
    main()
