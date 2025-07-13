import React, { useState, useEffect, useRef } from "react";
import {
    Stack,
    Text,
    Heading,
    Input,
    Flex,
    InputGroup,
    InputRightElement,
    CircularProgress,
    IconButton,
    Alert,
    AlertIcon,
} from "@chakra-ui/react";
import Sidebar from "../../components/Chat/ChatSidebar"; // Assuming this component exists
import Breadcrumbs from "../../components/Utility/Breadcrumbs"; // Assuming this component exists
import { TbSend } from "react-icons/tb";
import { useNavigate } from "react-router-dom"; // Import useNavigate for redirection

// --- Configuration ---
const API_BASE_URL = 'http://127.0.0.1:8000'; // Your backend URL

const ChatCounselling = () => {
    const [userText, setUserText] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    // --- State for User and Session IDs ---
    // These will be populated from localStorage on component mount.
    const [userId, setUserId] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    
    const chatEndRef = useRef(null);

    // --- Effect to load user and session info from localStorage ---
    useEffect(() => {
        const storedUserId = localStorage.getItem('userId');
        const storedSessionId = localStorage.getItem('sessionId');

        if (storedUserId && storedSessionId) {
            setUserId(storedUserId);
            setSessionId(storedSessionId);
        } else {
            // If user info is not found, they are not logged in.
            setError("Authentication error: You must be logged in to chat.");
            // Optional: Redirect to login page after a delay
            setTimeout(() => {
                navigate("/"); 
            }, 3000);
        }
    }, [navigate]); // Add navigate to dependency array

    // Effect to scroll to the bottom of the chat on new messages
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    // --- Function to send a message to the backend ---
    const sendMessage = async () => {
        // Prevent sending if not logged in, no text, or already loading
        if (!userText.trim() || !userId || !sessionId || loading) return; 
        
        setLoading(true);
        setError(null);

        const newUserMessage = { role: "user", content: userText };
        setMessages((prev) => [...prev, newUserMessage]);

        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                // Use the IDs retrieved from localStorage
                body: JSON.stringify({
                    user_id: userId,
                    session_id: sessionId,
                    message: userText,
                }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || `Error: ${response.statusText}`);
            }

            const data = await response.json();
            const assistantMessage = { role: "assistant", content: data.response };

            setMessages((prev) => [...prev, assistantMessage]);

        } catch (err) {
            const errorMessage = `Sorry, something went wrong. Please try again. Error: ${err.message}`;
            setError(errorMessage);
            setMessages((prev) => [
                ...prev,
                { role: "assistant", content: errorMessage },
            ]);
        } finally {
            setLoading(false);
            setUserText("");
        }
    };

    return (
        <Sidebar>
            <Breadcrumbs links={["Home", "Dashboard", "Counselling"]} />
            <Heading mt={8} ml={4}>
                Multi-Agentic Conversational AI System
            </Heading>
            <Stack p={4} gap={3} h="80vh">
                <Flex
                    flex={1}
                    direction="column"
                    pt={4}
                    bg="white"
                    w="full"
                    p={8}
                    borderRadius="md"
                    h="full"
                    overflowY="scroll"
                    sx={{
                        '&::-webkit-scrollbar': { width: '0' },
                        'scrollbarWidth': 'none',
                    }}
                >
                    {messages.map((msg, index) => (
                        <Flex
                            key={index}
                            bg={msg.role === "user" ? "blue.100" : "red.100"}
                            w="fit-content"
                            maxW="80%"
                            p={3}
                            m={1}
                            borderRadius={5}
                            alignSelf={msg.role === "user" ? "flex-end" : "flex-start"}
                            whiteSpace="pre-wrap"
                        >
                            <Text color="gray.800">{msg.content}</Text>
                        </Flex>
                    ))}
                    <div ref={chatEndRef} />
                </Flex>
                {error && !messages.length && ( // Only show main error if chat is empty
                    <Alert status="error">
                        <AlertIcon />
                        {error}
                    </Alert>
                )}
                <InputGroup size="lg">
                    <Input
                        value={userText}
                        disabled={loading || !userId} // Disable if not logged in
                        onChange={(e) => setUserText(e.target.value)}
                        pr="4.5rem"
                        placeholder={
                            loading ? "Processing..." : (userId ? "Ask anything related to your CSV..." : "Please log in to start chatting.")
                        }
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                sendMessage();
                            }
                        }}
                        as="textarea"
                        rows={2}
                        resize="none"
                        bg="white"
                        color="gray.800"
                    />
                    <InputRightElement width="4.5rem" h="full">
                        <IconButton
                            aria-label="Send message"
                            icon={loading ? <CircularProgress isIndeterminate size="20px" /> : <TbSend />}
                            isDisabled={loading || !userId}
                            onClick={sendMessage}
                            colorScheme="red"
                            h="80%"
                            mr={2}
                        />
                    </InputRightElement>
                </InputGroup>
            </Stack>
        </Sidebar>
    );
};

export default ChatCounselling;
