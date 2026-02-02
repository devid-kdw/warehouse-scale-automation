import { createTheme, MantineColorsTuple } from '@mantine/core';

// Enikon Palette
// primaryDark: #075282
// primaryMid: #2A6C9C
// accentLight: #468ABB
// accentPale: #83A9C3
// neutralGrey: #C9D0D6
// bgOffWhite: #F3F5F6

const enikonBlue: MantineColorsTuple = [
    '#eefeef', // 0
    '#d6e6f5', // 1
    '#83A9C3', // 2 - Accent Pale
    '#468ABB', // 3 - Accent Light
    '#2A6C9C', // 4 - Primary Mid
    '#075282', // 5 - Primary Dark (Main Brand)
    '#054066', // 6
    '#04324f', // 7
    '#022439', // 8
    '#011624'  // 9
];

export const theme = createTheme({
    primaryColor: 'enikonBlue',
    colors: {
        enikonBlue,
    },
    fontFamily: 'Roboto, Inter, sans-serif',
    defaultRadius: 'xs', // "Internal tool" feel, usually more squared
    components: {
        Button: {
            defaultProps: {
                color: 'enikonBlue.5', // Default buttons to Primary Dark
            },
        },
        AppShell: {
            styles: {
                main: {
                    backgroundColor: '#F3F5F6', // bgOffWhite
                },
                header: {
                    backgroundColor: '#075282', // primaryDark
                    color: 'white'
                }
            }
        }
    }
});
