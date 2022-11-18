import os
from datetime import datetime

from pandas import DataFrame

from local_module.scraper import ALL_PRODUCTS, PRODUCT_DETAIL


def main():
    ap = ALL_PRODUCTS()
    ap_url_list: list = ap.get_all_products()
    pd = PRODUCT_DETAIL(url_list=ap_url_list)
    table_list: list = pd.get_detail()
    df: DataFrame = DataFrame(table_list)
    now = datetime.now()
    output_dir: str = f"./output/{now:%Y}"
    os.makedirs(output_dir, exist_ok=True)
    df.to_csv(f"{output_dir}/{now:%Y%m%d_%H%M%S}.tsv", sep="\t")


if __name__ == "__main__":
    main()
