"use client";

import type { Message } from "ai";
import { motion } from "framer-motion";
import { HeartPulse } from "lucide-react";
import { useEffect, useState } from "react";

import { Markdown } from "./markdown";
import { PreviewAttachment } from "./preview-attachment";
import { cn } from "@/lib/utils";

// Interface estendida para mensagens com arquivos
interface MessageWithFiles extends Message {
  files?: Array<{
    name: string;
    url: string;
  }>;
}

export const PreviewMessage = ({
  message,
}: {
  chatId: string;
  message: MessageWithFiles;
  isLoading: boolean;
}) => {
  const [displayedContent, setDisplayedContent] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    setDisplayedContent(message.content || "");
    setIsTyping(false);
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
          {/* Renderizar arquivos usando o componente PreviewAttachment existente */}
          {message.files && message.files.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {message.files.map((file, index) => (
                <PreviewAttachment
                  key={index}
                  attachment={{
                    name: file.name,
                    url: file.url,
                    contentType: file.name.match(/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/i) ? 
                      `image/${file.name.split('.').pop()?.toLowerCase()}` : 
                      'application/octet-stream'
                  }}
                  isUploading={false}
                  showRemoveButton={false}
                />
              ))}
            </div>
          )}
          
          {message.content && displayedContent && (
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
