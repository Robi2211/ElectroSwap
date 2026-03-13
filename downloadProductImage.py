"""Download product images from the web and save them locally.

Usage:
    python downloadProductImage.py <filename>
    python downloadProductImage.py --all

Downloads royalty-free product images and saves them into
./static/images/products/ and ./static/images/categories/.

This script uses direct URLs to real, relevant product photos from
royalty-free sources (Unsplash, Pexels, Pixabay CDN links).
"""

import os
import sys
import requests

# Directories for saved images
PRODUCT_DIR = os.path.join(os.path.dirname(__file__), "static", "images", "products")
CATEGORY_DIR = os.path.join(os.path.dirname(__file__), "static", "images", "categories")

# Real product image URLs mapped to local filenames.
# These are direct links to royalty-free images from Unsplash.
PRODUCT_IMAGES = {
    "ryzen-9-7950x.jpg": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=600&h=400&fit=crop",
    "i9-14900k.jpg": "https://images.unsplash.com/photo-1555617981-dac3880eac6e?w=600&h=400&fit=crop",
    "ryzen-7-7800x3d.jpg": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop",
    "rtx-4090.jpg": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=600&h=400&fit=crop",
    "rx-7900-xtx.jpg": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&h=400&fit=crop",
    "rtx-4070-ti.jpg": "https://images.unsplash.com/photo-1623126908029-58cb08a2b272?w=600&h=400&fit=crop",
    "odyssey-g9.jpg": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&h=400&fit=crop",
    "lg-27gp950.jpg": "https://images.unsplash.com/photo-1585792180666-f7347c490ee2?w=600&h=400&fit=crop",
    "x670e-hero.jpg": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
    "z790-tomahawk.jpg": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=600&h=400&fit=crop",
    "trident-z5.jpg": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=600&h=400&fit=crop",
    "vengeance-ddr5.jpg": "https://images.unsplash.com/photo-1541029071515-84cc54f84dc5?w=600&h=400&fit=crop",
    "rm1000x.jpg": "https://images.unsplash.com/photo-1600348712270-3b0bdc82a1c3?w=600&h=400&fit=crop",
    "990-pro.jpg": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600&h=400&fit=crop",
    "sn850x.jpg": "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?w=600&h=400&fit=crop",
    "o11-dynamic.jpg": "https://images.unsplash.com/photo-1587202372616-b43abea06c2a?w=600&h=400&fit=crop",
    "noctua-nh-d15.jpg": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=600&h=400&fit=crop",
    "corsair-h150i.jpg": "https://images.unsplash.com/photo-1587202372583-49330a15584d?w=600&h=400&fit=crop",
    "gpx-superlight-2.jpg": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&h=400&fit=crop",
    "keychron-q1-pro.jpg": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=600&h=400&fit=crop",
    "rog-xg27aq.jpg": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=600&h=400&fit=crop",
}

# Category icon image URLs - hardware-themed images for each category
CATEGORY_IMAGES = {
    "cpu.jpg": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400&h=400&fit=crop",
    "gpu.jpg": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?w=400&h=400&fit=crop",
    "monitor.jpg": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=400&h=400&fit=crop",
    "motherboard.jpg": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=400&fit=crop",
    "psu.jpg": "https://images.unsplash.com/photo-1600348712270-3b0bdc82a1c3?w=400&h=400&fit=crop",
    "ram.jpg": "https://images.unsplash.com/photo-1562976540-1502c2145186?w=400&h=400&fit=crop",
    "case.jpg": "https://images.unsplash.com/photo-1587202372616-b43abea06c2a?w=400&h=400&fit=crop",
    "storage.jpg": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=400&h=400&fit=crop",
    "cooling.jpg": "https://images.unsplash.com/photo-1587202372634-32705e3bf49c?w=400&h=400&fit=crop",
    "peripherals.jpg": "https://images.unsplash.com/photo-1595225476474-87563907a212?w=400&h=400&fit=crop",
}


def download_image(url, filepath):
    """Download an image from the given URL and save it to filepath."""
    try:
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"  Downloaded: {filepath}")
        return True
    except requests.RequestException as e:
        print(f"  Failed to download {url}: {e}")
        return False


def download_single(filename):
    """Download a single product image by filename."""
    if filename in PRODUCT_IMAGES:
        filepath = os.path.join(PRODUCT_DIR, filename)
        return download_image(PRODUCT_IMAGES[filename], filepath)
    elif filename in CATEGORY_IMAGES:
        filepath = os.path.join(CATEGORY_DIR, filename)
        return download_image(CATEGORY_IMAGES[filename], filepath)
    else:
        print(f"Unknown filename: {filename}")
        print("Available product images:", ", ".join(sorted(PRODUCT_IMAGES.keys())))
        print("Available category images:", ", ".join(sorted(CATEGORY_IMAGES.keys())))
        return False


def download_all():
    """Download all product and category images."""
    os.makedirs(PRODUCT_DIR, exist_ok=True)
    os.makedirs(CATEGORY_DIR, exist_ok=True)

    print("Downloading product images...")
    success = 0
    for filename, url in PRODUCT_IMAGES.items():
        filepath = os.path.join(PRODUCT_DIR, filename)
        if os.path.exists(filepath):
            print(f"  Skipped (exists): {filepath}")
            success += 1
            continue
        if download_image(url, filepath):
            success += 1
    print(f"  Products: {success}/{len(PRODUCT_IMAGES)}")

    print("Downloading category images...")
    success = 0
    for filename, url in CATEGORY_IMAGES.items():
        filepath = os.path.join(CATEGORY_DIR, filename)
        if os.path.exists(filepath):
            print(f"  Skipped (exists): {filepath}")
            success += 1
            continue
        if download_image(url, filepath):
            success += 1
    print(f"  Categories: {success}/{len(CATEGORY_IMAGES)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python downloadProductImage.py <filename>")
        print("       python downloadProductImage.py --all")
        sys.exit(1)

    arg = sys.argv[1]
    if arg == "--all":
        download_all()
    else:
        download_single(arg)
    print("Done.")
