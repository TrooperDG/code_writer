function addThreeNumbers(a, b, c) {
  if (typeof a !== 'number' || typeof b !== 'number' || typeof c !== 'number') {
    throw new TypeError('All arguments must be numbers');
  }
  return a + b + c;
}