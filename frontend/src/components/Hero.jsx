import React, { useState, useRef } from "react";
import {
  Stack,
  Heading,
  Button,
  Container,
  Image,
  Flex,
  Box,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useToast,
  Text,
  Icon,
  Alert,
  AlertIcon,
  InputGroup,
  InputRightElement,
} from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import crm from "../assets/crm.svg"

// --- Configuration ---
const API_BASE_URL = 'http://127.0.0.1:8000'; // Ensure your backend is running at this address
const generateSessionId = () => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

// --- Custom SVG Icon for File Upload ---
const FileUploadIcon = (props) => (
  <Icon viewBox="0 0 24 24" {...props}>
    <path
      fill="currentColor"
      d="M19.35 10.04C18.67 6.59 15.64 4 12 4C9.11 4 6.6 5.64 5.35 8.04C2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5c0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"
    />
  </Icon>
);

// --- Authentication Modal Component ---
const AuthModal = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const toast = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const fileInputRef = useRef();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  // --- SIGN IN LOGIC ---
  const handleSignIn = async () => {
    if (!file) {
      setError("Please upload a CSV knowledge base file to sign in.");
      return;
    }
    setIsLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("email", email);
    formData.append("password", password);
    formData.append("file", file);

    try {
      // Use the combined login and upload endpoint
      const response = await fetch(`${API_BASE_URL}/api/v1/crm/login`, {
        method: "POST",
        body: formData, // Sending as multipart/form-data
      });

      if (response.ok) {
        const userData = await response.json();
        
        // --- FIX: Save user ID and a new session ID to localStorage ---
        localStorage.setItem('userId', userData.id);
        localStorage.setItem('sessionId', generateSessionId());
        // ----------------------------------------------------------------

        toast({
          title: "Login Successful",
          description: `Welcome back, ${userData.name || userData.email}! Knowledge base updated.`,
          status: "success",
          duration: 3000,
          isClosable: true,
        });
        navigate("/user/dashboard/");
      } else {
        const errData = await response.json();
        throw new Error(errData.detail || "Login failed.");
      }
    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  // --- SIGN UP LOGIC ---
  const handleSignUp = async () => {
    setIsLoading(true);
    setError("");

    try {
      // Only create the user, no file upload needed here.
      const userResponse = await fetch(`${API_BASE_URL}/api/v1/crm/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, company, password }),
      });

      if (!userResponse.ok) {
        const errData = await userResponse.json();
        throw new Error(errData.detail || "Failed to create user.");
      }
      
      toast({
        title: "Account Created!",
        description: "You can now sign in with your new credentials.",
        status: "success",
        duration: 4000,
        isClosable: true,
      });
      onClose();

    } catch (err) {
      setError(err.message);
    }
    setIsLoading(false);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} isCentered>
      <ModalOverlay />
      <ModalContent bg="gray.50">
        <ModalHeader color="gray.800">Get Started</ModalHeader>
        <ModalCloseButton color="gray.800" />
        <ModalBody>
          <Tabs isFitted variant="enclosed-colored" colorScheme="red">
            <TabList>
              <Tab _selected={{ color: "white", bg: "red.500" }}>Sign In</Tab>
              <Tab _selected={{ color: "white", bg: "red.500" }}>Sign Up</Tab>
            </TabList>
            <TabPanels>
              {/* Sign In Panel */}
              <TabPanel>
                <VStack as="form" spacing={4} color="gray.800" onSubmit={(e) => { e.preventDefault(); handleSignIn(); }}>
                  <FormControl isRequired>
                    <FormLabel>Email Address</FormLabel>
                    <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
                  </FormControl>
                  <FormControl isRequired>
                    <FormLabel>Password</FormLabel>
                    <InputGroup>
                      <Input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
                      <InputRightElement width="4.5rem">
                        <Button h="1.75rem" size="sm" onClick={() => setShowPassword(!showPassword)}>
                          {showPassword ? "Hide" : "Show"}
                        </Button>
                      </InputRightElement>
                    </InputGroup>
                  </FormControl>
                  <FormControl isRequired>
                    <FormLabel>Upload Knowledge Base (CSV)</FormLabel>
                    <Button w="full" variant="outline" colorScheme="gray" leftIcon={<FileUploadIcon />} onClick={() => fileInputRef.current.click()}>
                      {file ? file.name : "Select File"}
                    </Button>
                    <Input type="file" ref={fileInputRef} onChange={handleFileChange} accept=".csv" style={{ display: "none" }}/>
                  </FormControl>
                  <Button type="submit" colorScheme="red" w="full" isLoading={isLoading}>
                    Sign In & Start
                  </Button>
                </VStack>
              </TabPanel>
              {/* Sign Up Panel */}
              <TabPanel>
                <VStack as="form" spacing={4} color="gray.800" onSubmit={(e) => { e.preventDefault(); handleSignUp(); }}>
                  <FormControl isRequired>
                    <FormLabel>Name</FormLabel>
                    <Input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="John Doe" />
                  </FormControl>
                  <FormControl>
                    <FormLabel>Company (Optional)</FormLabel>
                    <Input type="text" value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Example Inc." />
                  </FormControl>
                  <FormControl isRequired>
                    <FormLabel>Email Address</FormLabel>
                    <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
                  </FormControl>
                   <FormControl isRequired>
                    <FormLabel>Password</FormLabel>
                     <InputGroup>
                      <Input type={showPassword ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
                      <InputRightElement width="4.5rem">
                        <Button h="1.75rem" size="sm" onClick={() => setShowPassword(!showPassword)}>
                          {showPassword ? "Hide" : "Show"}
                        </Button>
                      </InputRightElement>
                    </InputGroup>
                  </FormControl>
                  <Button type="submit" colorScheme="red" w="full" isLoading={isLoading}>
                    Create Account
                  </Button>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
          {error && (
            <Alert status="error" mt={4} rounded="md">
              <AlertIcon />
              <Text color="gray.800">{error}</Text>
            </Alert>
          )}
        </ModalBody>
        <ModalFooter />
      </ModalContent>
    </Modal>
  );
};

// --- Main Hero Component ---
const Hero = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  return (
    <>
      <Container maxW="container.xl" bg="red.50">
        <Stack direction={{ base: "column", md: "row" }} py={8}>
          <Flex flex="1">
            <Stack justifyContent="center" gap={8}>
              <Box maxW="50ch">
                <Heading fontSize={{ base: "3xl", md: "4xl", lg: "5xl" }} color="gray.800">
                    Multi Agentic Conversational AI System
                </Heading>
              </Box>
              <Stack direction="row" gap={8}>
                <Button colorScheme="red" p={4} onClick={onOpen}>
                  Start Chatting
                </Button>
              </Stack>
            </Stack>
          </Flex>
          <Flex flex="0.75" pt={{ base: 4, md: 0 }}>
            <img src={crm}  width="100%"/>
          </Flex>
        </Stack>
      </Container>
      
      <AuthModal isOpen={isOpen} onClose={onClose} />
    </>
  );
};

export default Hero;
