function myFunction() {
    // Declare variables
    var input, filter, ul, li, a, i;
    input = document.getElementById('inputClass');
    filter = input.value.toUpperCase();
    ul = document.getElementById("myUL");
    li = ul.getElementsByTagName('li');
    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        decoded = a.innerHTML.replace(/&amp;/g, '&');
        if (decoded.toUpperCase().indexOf(filter) > -1) {
            console.log(a.innerHTML);
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}
function complete(description, id) {
  	document.getElementById('inputClass').value = description;
  	document.getElementById('hiddenInputClass').value = id;
}			