"use client";

import type { Message } from "ai";
import { motion } from "framer-motion";
import { HeartPulse } from "lucide-react";
import { useEffect, useState } from "react";

import { Markdown } from "./markdown";
import { cn } from "@/lib/utils";

export const PreviewMessage = ({
  message,
}: {
  chatId: string;
  message: Message;
  isLoading: boolean;
}) => {
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    if (message.role === "assistant" && message.content) {
      let charIndex = 0;
      setDisplayedContent("");
      setIsTyping(true);

      const intervalId = setInterval(() => {
        if (charIndex < message.content.length) {
          setDisplayedContent((prev) => prev + message.content[charIndex]);
          charIndex++;
        } else {
          clearInterval(intervalId);
          setIsTyping(false);
        }
      }, 15);

      return () => clearInterval(intervalId);
    } else {
      setDisplayedContent(message.content);
      setIsTyping(false);
    }
  }, [message.content, message.role]);

  return (
    <motion.div
      className="w-full mx-auto max-w-3xl px-4 group/message"
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      data-role={message.role}
    >
      <div
        className={cn(
          "group-data-[role=user]/message:bg-primary group-data-[role=user]/message:text-primary-foreground flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-2xl group-data-[role=user]/message:py-2 rounded-xl",
        )}
      >
        {message.role === "assistant" && (
          <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-border">
            <HeartPulse size={14} />
          </div>
        )}

        <div className="flex flex-col gap-2 w-full">
          {message.content && (
            <div className="flex flex-col gap-4">
              <Markdown>{displayedContent}</Markdown>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const ThinkingMessage = () => {
  const role = "assistant";

  return (
    <motion.div
      className="w-full mx-auto max-w-3xl px-4 group/message "
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1, transition: { delay: 1 } }}
      data-role={role}
    >
      <div
        className={cn(
          "flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-2xl group-data-[role=user]/message:py-2 rounded-xl",
          {
            "group-data-[role=user]/message:bg-muted": true,
          },
        )}
      >
        <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-border">
          <HeartPulse size={14} className="animate-pulse" />
        </div>

        <div className="flex flex-col gap-2 w-full">
          <div className="flex flex-col gap-4 text-muted-foreground">
            Thinking...
          </div>
        </div>
      </div>
    </motion.div>
  );
};
