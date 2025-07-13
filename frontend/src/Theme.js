import { extendTheme } from "@chakra-ui/react"
const theme = extendTheme({
    initialColorMode: "light",
    useSystemColorMode: false,
    styles: {
        global: (props) => ({
            '&::-webkit-scrollbar': { width: "0.75rem", bg: props.colorMode === "dark" ? "#1A202C" : "#f5f5f5" },
            '&::-webkit-scrollbar-track': {bg: "red.50",borderRadius: "3rem" },
            '&::-webkit-scrollbar-thumb': { bg: props.colorMode === "dark" ? "#3f444e" : "red.400",borderRadius: "3rem" },
        }),
    },

})

export default theme
