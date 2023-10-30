function binary_search_recurse(arr, l, r, substr) {
  if (r >= l) {
    var mid = Math.floor((l + r) / 2);
    if (arr[mid].startsWith(substr)) {
      return mid;
    }
    if (arr[mid] > substr) {
      return binary_search_recurse(arr, l, mid - 1, substr);
    }
    return binary_search_recurse(arr, mid + 1, r, substr);
  }
  return -1;
}

function binary_search(arr, substr) {
  return binary_search_recurse(arr, 0, arr.length - 1, substr);
}

function suggest(substr) {
  var res = binary_search(window.tags_sorted, substr);
  if (res == -1) {
    return [];
  } else {
    var options = [];
    var i = res;
    while (i < tags_sorted.length && tags_sorted[i].startsWith(substr)) {
      options.push(tags_sorted[i]);
      i++;
    }
    return options;
  }
}

function suggest_input(input_id) {
  var input = document.getElementById(input_id);
  var datalist = document.getElementById(input_id + "-options");
  var value = input.value.replaceAll(' ', '_').toUpperCase();
  datalist.innerHTML = "";
  var options = suggest(value);
  for (var i = 0; i < options.length; i++) {
     var option = document.createElement("option");
     option.value = options[i].replaceAll('_', ' ').toLowerCase();
     datalist.appendChild(option);
  }
}