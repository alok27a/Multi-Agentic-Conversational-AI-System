import React from "react";
import {
  Box,
  Container,
  Flex,
  HStack,
  Button
} from "@chakra-ui/react";
import logo from '../../assets/image.png';

const Navbar = () => {
  return (
    <Box px={4}>
      <Container maxW="container.xl" py={4}>
        <Flex direction="column" alignItems="center" justifyContent="center" gap={4}>
          <HStack>
            <img src={logo} alt="Logo" width="9%" />
           
          </HStack>
          {/* <Button colorScheme="red">Click Me</Button> */}
        </Flex>
      </Container>
    </Box>
  );
};

export default Navbar;
