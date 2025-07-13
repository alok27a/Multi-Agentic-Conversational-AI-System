import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import Home from "./pages/Home";
import Theme from "./Theme"

import ChatCounselling from "./pages/Chat/ChatCounselling";
import History from "./pages/Chat/ChatHistory";


const App = () => {
  return (
    <ChakraProvider theme={Theme}>
      <BrowserRouter>
        <Routes>
          <Route exact path="/" element={<Home />} />

          <Route exact path="/user/dashboard">
            <Route index element={<ChatCounselling />} />
            <Route path="history" element={<History />} />
          </Route>

        </Routes>
      </BrowserRouter>
    </ChakraProvider>
  );
};

export default App;
