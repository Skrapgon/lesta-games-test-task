let textId = null;
let offset = 0;
const limit = 50;
let curPage = 1;

let select;
let currentOptions = new Set();

document.addEventListener("DOMContentLoaded", function () {
    select = document.getElementById("textSelect");
    select.addEventListener("change", function () {
        const selectedIndex = this.selectedIndex;
        this.value;
        if (selectedIndex > 0) {
            textId = this.value;
            changePage(0);
        }
    });
});

function areSetsEqual(setA, setB) {
    if (setA.size !== setB.size) return false;
    for (let item of setA) {
        if (!setB.has(item)) return false;
    }
    return true;
}

async function loadOptions() {

    const response = await fetch("/api/texts/", {
        method: "GET"
    });

    const data = await response.json();

    const newOptionsSet = new Set(data);
    const selectedValue = select.value;

    if (!areSetsEqual(currentOptions, newOptionsSet)) {
        updateSelect(data, selectedValue);
        currentOptions = newOptionsSet;
    }
}

async function updateSelect(data, selectedValue) {
    select.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.textContent = "Choose text";
    select.appendChild(defaultOption);

    data.forEach(item => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = `${item.text_str.slice(0, 30)}... (ID: ${item.id})`;
        option.title = item.text_str;
        
        if (item.id === selectedValue) {
        option.selected = true;
        }
        select.appendChild(option);
    });

    if (!select.value) {
        defaultOption.selected = true;
    }
}

async function updatePageNumber() {
    document.getElementById("page-number").textContent = `Page: ${curPage}`;
}

async function getWordsData(url) {
    const response = await fetch(url, {
        method: "GET"
    });
    
    if (!response.ok) {
        throw new Error(`Request Error: ${response.status}`);
    }
    
    return await response.json();
}

async function uploadFile(event) {
    event.preventDefault();
    const fileInput = document.getElementById("file");
    const file = fileInput.files[0];

    if (!file || file.type !== "text/plain") {
        alert("Please select a text file.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/api/texts/", {
        method: "POST",
        body: formData
    });

    const data = await response.json();
    if (data.id) {
        textId = data.id;
    }

    const wordsData = await getWordsData(`/api/texts/${textId}/?offset=${offset}&limit=${limit}`);
    renderTable(wordsData || []);
    loadOptions();
}

async function changePage(direction) {
    if (offset + direction * limit < 0) offset = 0;
    else{
        offset += direction * limit;
        curPage += direction;
    }

    if (!textId) return;

    const data = await getWordsData(`/api/texts/${textId}/?offset=${offset}&limit=${limit}`);
    if (!data.length) return;
    renderTable(data || []);
    
}

function renderTable(data) {
    updatePageNumber();
    
    const tableBody = document.getElementById("data-table-body");
    tableBody.innerHTML = "";

    data.forEach((row, index) => {
        const tr = document.createElement("tr");
        Object.values(row).forEach(val => {
            const td = document.createElement("td");
            td.textContent = val;
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}

loadOptions();
// setInterval(loadOptions, 5000);