import React, { useState, useEffect } from 'react';
import {
  Box,
  Text,
  Spinner,
  VStack,
  Icon,
  Heading,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Alert,
  AlertIcon,
  Flex,
  Tag,
  HStack,
} from '@chakra-ui/react';
import { MdChatBubbleOutline, MdErrorOutline } from 'react-icons/md';
import { useNavigate } from 'react-router-dom';
import Sidebar from '../../components/Chat/ChatSidebar'; // Assuming this is the correct path
import Breadcrumbs from '../../components/Utility/Breadcrumbs'; // Assuming this is the correct path

// --- Configuration ---
const API_BASE_URL = 'http://127.0.0.1:8000'; // Your backend URL

const ChatHistory = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      const userId = localStorage.getItem('userId');

      if (!userId) {
        setError("You must be logged in to view chat history.");
        setLoading(false);
        // Optional: Redirect to login page
        setTimeout(() => navigate('/'), 3000);
        return;
      }

      try {
        const response = await fetch(`${API_BASE_URL}/api/v1/crm/conversations/${userId}`);
        if (!response.ok) {
          const errData = await response.json();
          throw new Error(errData.detail || "Failed to fetch chat history.");
        }
        const data = await response.json();
        // Sort conversations by most recent first
        setConversations(data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at)));
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [navigate]);

  const renderContent = () => {
    if (loading) {
      return (
        <Box minH="70vh" display="flex" alignItems="center" justifyContent="center">
          <VStack spacing={4}>
            <Spinner size="xl" color="blue.500" />
            <Text fontSize="lg">Loading Chat History...</Text>
          </VStack>
        </Box>
      );
    }
  
    if (error) {
      return (
        <Box minH="70vh" display="flex" alignItems="center" justifyContent="center" p={4}>
          <Alert status="error" maxW="lg" borderRadius="md">
            <AlertIcon as={MdErrorOutline} />
            {error}
          </Alert>
        </Box>
      );
    }
  
    if (conversations.length === 0) {
      return (
        <Box minH="70vh" display="flex" alignItems="center" justifyContent="center">
          <VStack spacing={4} textAlign="center">
            <Icon as={MdChatBubbleOutline} boxSize={12} color="gray.400" />
            <Heading fontSize="2xl" fontWeight="bold">
              No Conversations Yet
            </Heading>
            <Text fontSize="md" color="gray.500">
              Your past conversations will appear here once you start chatting.
            </Text>
          </VStack>
        </Box>
      );
    }
  
    return (
      <Box p={8}>
        <Heading mb={6}>Your Conversation History</Heading>
        <Accordion allowToggle>
          {conversations.map((convo) => (
            <AccordionItem key={convo.id} bg="white" borderRadius="md" mb={4} shadow="sm">
              <h2>
                <AccordionButton _expanded={{ bg: 'red.500', color: 'white' }}>
                  <Box flex="1" textAlign="left">
                    <Text fontWeight="bold" noOfLines={1}>
                      {convo.messages[0]?.content || 'Empty Conversation'}
                    </Text>
                    <Text fontSize="sm" color="gray.500" _dark={{ color: 'gray.200' }}>
                      {new Date(convo.created_at).toLocaleString()}
                    </Text>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <VStack spacing={4} align="stretch">
                  {convo.messages.map((msg, index) => (
                    <Flex
                      key={index}
                      bg={msg.role === 'user' ? 'blue.100' : 'gray.100'}
                      w="fit-content"
                      maxW="80%"
                      p={3}
                      borderRadius="lg"
                      alignSelf={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                    >
                      <Text whiteSpace="pre-wrap" color="gray.800">{msg.content}</Text>
                    </Flex>
                  ))}
                </VStack>
                <HStack mt={4} spacing={2}>
                    <Text fontSize="sm" fontWeight="bold">Tags:</Text>
                    {convo.tags.length > 0 ? convo.tags.map(tag => (
                        <Tag key={tag} size="sm" variant="solid" colorScheme="purple">{tag}</Tag>
                    )) : <Tag size="sm">No tags yet</Tag>}
                </HStack>
              </AccordionPanel>
            </AccordionItem>
          ))}
        </Accordion>
      </Box>
    );
  }

  return (
    <Sidebar>
        <Breadcrumbs links={["Home", "Dashboard", "History"]} />
        {renderContent()}
    </Sidebar>
  );
};

export default ChatHistory;
