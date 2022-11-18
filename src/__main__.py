from local_module.scraper import ALL_PRODUCTS, PRODUCT_DETAIL


def main():
    ap = ALL_PRODUCTS()
    ap_url_list: list = ap.get_all_products()
    pd = PRODUCT_DETAIL(url_list=ap_url_list)
    pd.get_detail()


if __name__ == "__main__":
    main()
