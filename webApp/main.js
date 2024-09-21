function controlFromInput(fromSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#8B0000', controlSlider);
    if (from > to) {
        fromSlider.value = to;
        fromInput.value = to;
    } else {
        fromSlider.value = from;
    }
}
    
function controlToInput(toSlider, fromInput, toInput, controlSlider) {
    const [from, to] = getParsed(fromInput, toInput);
    fillSlider(fromInput, toInput, '#C6C6C6', '#8B0000', controlSlider);
    setToggleAccessible(toInput);
    if (from <= to) {
        toSlider.value = to;
        toInput.value = to;
    } else {
        toInput.value = from;
    }
}

function controlFromSlider(fromSlider, toSlider, fromInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#8B0000', toSlider);
  if (from > to) {
    fromSlider.value = to;
    fromInput.value = to;
  } else {
    fromInput.value = from;
  }
}

function controlToSlider(fromSlider, toSlider, toInput) {
  const [from, to] = getParsed(fromSlider, toSlider);
  fillSlider(fromSlider, toSlider, '#C6C6C6', '#8B0000', toSlider);
  setToggleAccessible(toSlider);
  if (from <= to) {
    toSlider.value = to;
    toInput.value = to;
  } else {
    toInput.value = from;
    toSlider.value = from;
  }
}

function getParsed(currentFrom, currentTo) {
  const from = parseInt(currentFrom.value, 10);
  const to = parseInt(currentTo.value, 10);
  return [from, to];
}

function fillSlider(from, to, sliderColor, rangeColor, controlSlider) {
    const rangeDistance = to.max-to.min;
    const fromPosition = from.value - to.min;
    const toPosition = to.value - to.min;
    controlSlider.style.background = `linear-gradient(
      to right,
      ${sliderColor} 0%,
      ${sliderColor} ${(fromPosition)/(rangeDistance)*100}%,
      ${rangeColor} ${((fromPosition)/(rangeDistance))*100}%,
      ${rangeColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} ${(toPosition)/(rangeDistance)*100}%, 
      ${sliderColor} 100%)`;
}

function setToggleAccessible(currentTarget) {
  const toSlider = document.querySelector('#toSlider');
  if (Number(currentTarget.value) <= 0 ) {
    toSlider.style.zIndex = 2;
  } else {
    toSlider.style.zIndex = 0;
  }
}



const fromSlider = document.querySelector('#fromSlider');
const toSlider = document.querySelector('#toSlider');
const fromInput = document.querySelector('#fromInput');
const toInput = document.querySelector('#toInput');
fillSlider(fromSlider, toSlider, '#C6C6C6', '#8B0000', toSlider);
setToggleAccessible(toSlider);

fromSlider.oninput = () => controlFromSlider(fromSlider, toSlider, fromInput);
toSlider.oninput = () => controlToSlider(fromSlider, toSlider, toInput);
fromInput.oninput = () => controlFromInput(fromSlider, fromInput, toInput, toSlider);
toInput.oninput = () => controlToInput(toSlider, fromInput, toInput, toSlider);


let lastClickedItemType = null; // Track the last clicked item type
let lastClickedRarity = null; // Track the last clicked rarity

// Handle item type button clicks
document.querySelectorAll('.item-btn').forEach(button => {
    button.addEventListener('click', function() {
        if (lastClickedItemType) {
            lastClickedItemType.classList.remove('active');
        }
        this.classList.toggle('active');
        lastClickedItemType = this;
        document.getElementById('lastClickedInfo_item').textContent = `Dernier bouton cliqué : ${this.textContent}`;
    });
});

// Handle rarity button clicks
document.querySelectorAll('.rarity-btn').forEach(button => {
    button.addEventListener('click', function() {
        if (lastClickedRarity) {
            lastClickedRarity.classList.remove('active');
        }
        this.classList.toggle('active');
        lastClickedRarity = this;
        document.getElementById('lastClickedInfo_rarity').textContent = `Dernier bouton cliqué : ${this.textContent}`;
    });
});

// Fetch button click event
document.getElementById('fetchButton').addEventListener('click', function() {
    if (!lastClickedItemType || !lastClickedRarity) {
        lastClickedItemType = null
        lastClickedRarity = null

    }

    const lvl_min = parseInt(fromSlider.value, 10); // Get min level from the slider
    const lvl_max = parseInt(toSlider.value, 10); 
    const item_type = lastClickedItemType.value; // Get selected item type
    const rarity = lastClickedRarity.value; // Get selected rarity
    const number_results = 10; // Adjust as necessary


    fetch(`http://localhost:5000/get_items?lvl_min=${lvl_min}&lvl_max=${lvl_max}&item_type=${item_type}&rarity=${rarity}&number_results=${number_results}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = ''; // Clear previous results

            data.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'item';
                
                // Set the inner HTML structure with item details
                itemDiv.innerHTML = `
                    <strong>${item.name}</strong> (${item.rarity}) - ${item.count} times 
                    <img src="${item.img}" width="50">
                `;
            
                // Apply background color based on rarity
                switch (item.rarity) {
                    case 'common':
                        itemDiv.style.backgroundColor = '#cccecf'; // Light gray for Common
                        break;
                    case 'rare':
                        itemDiv.style.backgroundColor = '#218b02'; // Green for Rare
                        break;
                    case 'mythic':
                        itemDiv.style.backgroundColor = '#fdb033'; // Orange for Mythic
                        break;
                    case 'legendary':
                        itemDiv.style.backgroundColor = '#fcef70'; // Yellow for Legendary
                        break;
                    case 'relic':
                        itemDiv.style.backgroundColor = '#874499'; // Purple for Relic
                        break;
                    case 'epic':
                        itemDiv.style.backgroundColor = '#d06beb'; // Light purple for Epic
                        break;
                    case 'memory':
                        itemDiv.style.backgroundColor = '#53b7d0'; // Light blue for Memory
                        break;
                    default:
                        itemDiv.style.backgroundColor = '#ffffff'; // White for undefined rarities
                }
            
                // Append the dynamically created item to the resultsDiv (parent container)
                resultsDiv.appendChild(itemDiv);
            });
        })
        .catch(error => console.error('Error fetching data:', error));
});