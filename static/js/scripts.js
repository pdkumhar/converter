// Handling drag and drop functionality
let dropArea = document.getElementById('drop-area');
let fileElem = document.getElementById('fileElem');
let fileNameDisplay = document.getElementById('file-name'); // File name display element

dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('hover');
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('hover');
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('hover');
    handleFiles(e.dataTransfer.files);
});

function handleFiles(files) {
    let file = files[0];
    if (file) {
        // Update file input with dropped file
        fileElem.files = files;

        // Display the selected file name
        fileNameDisplay.textContent = file.name;
    }
}
