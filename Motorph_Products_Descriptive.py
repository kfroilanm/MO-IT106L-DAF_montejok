{
  "metadata": {
    "kernelspec": {
      "name": "python",
      "display_name": "Python (Pyodide)",
      "language": "python"
    },
    "language_info": {
      "codemirror_mode": {
        "name": "python",
        "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.8"
    }
  },
  "nbformat_minor": 5,
  "nbformat": 4,
  "cells": [
    {
      "id": "711621eb-4316-40c1-b094-8fb468786f90",
      "cell_type": "code",
      "source": "import pandas as pd\ndf= pd.read_csv(\"MotorPH_Products_Preprocessed  - Sheet1.csv\")\ndf.head()",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "execution_count": 1,
          "output_type": "execute_result",
          "data": {
            "text/plain": "   Product ID Number               Product Name Product Type  Unit Price  \\\n0                  1              Honda CBR500R        Sport      389000   \n1                  2               Yamaha MT-15   Naked Bike      178000   \n2                  3         Kawasaki Ninja 400        Sport      340000   \n3                  4      Suzuki Raider R150 Fi    Underbone      119900   \n4                  5  Royal Enfield Classic 350      Classic      250000   \n\n   Date of Manufacturing  Date of Acquisition  \n0                   2021                 2023  \n1                   2022                 2023  \n2                   2023                 2024  \n3                   2020                 2021  \n4                   2022                 2023  ",
            "text/html": "<div>\n<style scoped>\n    .dataframe tbody tr th:only-of-type {\n        vertical-align: middle;\n    }\n\n    .dataframe tbody tr th {\n        vertical-align: top;\n    }\n\n    .dataframe thead th {\n        text-align: right;\n    }\n</style>\n<table border=\"1\" class=\"dataframe\">\n  <thead>\n    <tr style=\"text-align: right;\">\n      <th></th>\n      <th>Product ID Number</th>\n      <th>Product Name</th>\n      <th>Product Type</th>\n      <th>Unit Price</th>\n      <th>Date of Manufacturing</th>\n      <th>Date of Acquisition</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      <td>1</td>\n      <td>Honda CBR500R</td>\n      <td>Sport</td>\n      <td>389000</td>\n      <td>2021</td>\n      <td>2023</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>2</td>\n      <td>Yamaha MT-15</td>\n      <td>Naked Bike</td>\n      <td>178000</td>\n      <td>2022</td>\n      <td>2023</td>\n    </tr>\n    <tr>\n      <th>2</th>\n      <td>3</td>\n      <td>Kawasaki Ninja 400</td>\n      <td>Sport</td>\n      <td>340000</td>\n      <td>2023</td>\n      <td>2024</td>\n    </tr>\n    <tr>\n      <th>3</th>\n      <td>4</td>\n      <td>Suzuki Raider R150 Fi</td>\n      <td>Underbone</td>\n      <td>119900</td>\n      <td>2020</td>\n      <td>2021</td>\n    </tr>\n    <tr>\n      <th>4</th>\n      <td>5</td>\n      <td>Royal Enfield Classic 350</td>\n      <td>Classic</td>\n      <td>250000</td>\n      <td>2022</td>\n      <td>2023</td>\n    </tr>\n  </tbody>\n</table>\n</div>"
          },
          "metadata": {}
        }
      ],
      "execution_count": 1
    },
    {
      "id": "02fd1f61-189d-4198-af3b-0514dad52363",
      "cell_type": "code",
      "source": "total_products = len(df)\nprint(\"Total Number of Products:\", total_products)",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Total Number of Products: 50\n"
        }
      ],
      "execution_count": 13
    },
    {
      "id": "6ff30739-6ad4-44d1-9689-b092198d6299",
      "cell_type": "code",
      "source": "product_type_counts = df[\"Product Type\"].value_counts()\nprint(product_type_counts)",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Product Type\nScooter          12\nNaked Bike        7\nSport             4\nAdventure         4\nCruiser           4\nUnderbone         3\nDual-Sport        3\nCafe Racer        2\nCommuter          2\nHeritage          2\nClassic           1\nRetro             1\nSport Touring     1\nScrambler         1\nStandard          1\nTouring           1\nStreet            1\nName: count, dtype: int64\n"
        }
      ],
      "execution_count": 14
    },
    {
      "id": "74e41a19-3f3f-49f1-893a-f877e746b55e",
      "cell_type": "code",
      "source": "average_price = df[\"Unit Price\"].mean()\nminimum_price = df[\"Unit Price\"].min()\nmaximum_price = df[\"Unit Price\"].max()\n\nprint(\"Average Unit Price:\", average_price)\nprint(\"Minimum Unit Price:\", minimum_price)\nprint(\"Maximum Unit Price:\", maximum_price)",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Average Unit Price: 257872.0\nMinimum Unit Price: 48000\nMaximum Unit Price: 995000\n"
        }
      ],
      "execution_count": 15
    },
    {
      "id": "a42fa6cb-bf8c-4b19-9352-abd01e43fabc",
      "cell_type": "code",
      "source": "print(f\"Average Unit Price: ₱{average_price:,.2f}\")\nprint(f\"Minimum Unit Price: ₱{minimum_price:,.2f}\")\nprint(f\"Maximum Unit Price: ₱{maximum_price:,.2f}\")",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Average Unit Price: ₱257,872.00\nMinimum Unit Price: ₱48,000.00\nMaximum Unit Price: ₱995,000.00\n"
        }
      ],
      "execution_count": 16
    },
    {
      "id": "03db4954-0fb9-447c-8e7b-97ba0220fdae",
      "cell_type": "code",
      "source": "print(df.loc[df[\"Unit Price\"].idxmin(), [\"Product Name\", \"Unit Price\"]])\nprint(df.loc[df[\"Unit Price\"].idxmax(), [\"Product Name\", \"Unit Price\"]])",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Product Name    Rusi Flash 125\nUnit Price               48000\nName: 29, dtype: object\nProduct Name    BMW R nineT\nUnit Price           995000\nName: 40, dtype: object\n"
        }
      ],
      "execution_count": 17
    },
    {
      "id": "8c4586c2-60da-459e-837a-8cc972af8dda",
      "cell_type": "code",
      "source": "total_inventory_cost = df[\"Unit Price\"].sum()\nprint(f\"Total Inventory Cost: ₱{total_inventory_cost:,.2f}\")",
      "metadata": {
        "trusted": true
      },
      "outputs": [
        {
          "name": "stdout",
          "output_type": "stream",
          "text": "Total Inventory Cost: ₱12,893,600.00\n"
        }
      ],
      "execution_count": 18
    },
    {
      "id": "aac9cbda-24ac-400a-955f-fca4780b84f8",
      "cell_type": "code",
      "source": "",
      "metadata": {
        "trusted": true
      },
      "outputs": [],
      "execution_count": null
    }
  ]
}