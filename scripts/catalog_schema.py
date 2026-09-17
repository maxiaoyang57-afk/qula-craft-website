"""Category lists link to product pages; offers belong on verified PDPs only."""

BASE = "https://www.qulacrafts.com/"


def catalog_list_item(row, position):
    return {
        "@type": "ListItem",
        "position": position,
        "name": row.get("titleFull") or row["title"],
        "url": BASE + row["pdp"],
        "image": BASE + row["image"],
    }
