function addNumbers(num1, num2) {
  if (typeof num1 !== 'number' || typeof num2 !== 'number') {
    throw new TypeError('Both arguments must be numbers');
  }
  return num1 + num2;
}