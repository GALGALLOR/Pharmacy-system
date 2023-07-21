const searchInput = document.getElementById('searchInput');
const itemList = document.getElementById('itemList');
const items = itemList.getElementsByTagName('li');

searchInput.addEventListener('input', filterItems);

function filterItems() {
  const searchTerm = searchInput.value.toLowerCase();
  for (const item of items) {
    const itemName = item.textContent.toLowerCase();
    if (itemName.includes(searchTerm)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  }
}
