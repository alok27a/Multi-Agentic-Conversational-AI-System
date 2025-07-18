import React from "react";
import { Center, Text, Link } from "@chakra-ui/react";

const Footer = () => {
  return (
    <Center py={5} borderTop="1px" borderColor="gray.100">
      <Text>
        Made with ❤️ by Alok Mathur |{" "}
        <Link
          href="https://github.com/alok27a/"
          isExternal
          color="blue.500"
        >
          Github Repository
        </Link>
      </Text>
    </Center>
  );
};

export default Footer;
