export const tailwindColors = [
    'red', 'green', 'blue', 'yellow', 'purple', 'pink'
];

export const getColorForPlayer = (playerIndex) => {
    return tailwindColors[playerIndex % tailwindColors.length];
};