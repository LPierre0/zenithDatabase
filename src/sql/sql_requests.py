import sqlite3
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from io import BytesIO

def display_multiple_images(urls, names, save_path):
    num_images = len(urls)
    cols = 3  # Number of columns in the grid
    rows = (num_images + cols - 1) // cols  # Calculate number of rows needed

    fig, axes = plt.subplots(rows, cols, figsize=(6, 3 * rows))  # Adjusted figsize for smaller images

    for i, (url, name) in enumerate(zip(urls, names)):
        response = requests.get(url)
        img = mpimg.imread(BytesIO(response.content), format='webp')
        
        ax = axes[i // cols, i % cols]  # Get the current axis
        ax.imshow(img)
        ax.axis('off')  # Hide axes
        ax.set_title(name, fontsize=12)  # Add the image name as title
    
    # Hide any unused subplots
    for j in range(num_images, rows * cols):
        axes[j // cols, j % cols].axis('off')
    
    plt.tight_layout()
    plt.savefig(save_path)  # Save the plot to a file
    plt.close()  # Close the plot to free up memory



def get_best_items_of_level_range(lvl_min, lvl_max, item_type, limit=10):
    query = '''
        SELECT item.name, item.rarity, item.url, item.img, COUNT(*) as count_item
        FROM build
        JOIN item ON item.url = build.{item_type}_url
        WHERE build.lvl BETWEEN ? AND ?
        GROUP BY item.url
        ORDER BY count_item DESC
        LIMIT ?;
    '''
    
    with sqlite3.connect('db/zenithDatabase.sqlite') as conn:
        cursor = conn.cursor()
        cursor.execute(query.format(item_type=item_type), (lvl_min, lvl_max, limit))
        results = cursor.fetchall()
        list_urls = []
        list_names = []
        for row in results:
            print(row)
            list_names.append(row[0])
            list_urls.append(row[-2])

    display_multiple_images(list_urls, list_names, f'images/{item_type}-{lvl_min}-{lvl_max}.jpg')
if __name__ == "__main__":
    for item_type in ['casque', 'amulette', 'plastron', 'anneau1', 'anneau2', 'bottes', 'cape', 'epaulettes', 'ceinture', 'dague_or_bouclier_or_armes', 'armes', 'embleme']:
        get_best_items_of_level_range(0, 15, item_type)
        for i in range(21, 230, 15):
            get_best_items_of_level_range(i, i+14, item_type)
    
