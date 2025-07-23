import type { Attachment } from "ai";

import { LoaderIcon, TrashIcon } from "./icons";
import { cn } from "@/lib/utils";

export const PreviewAttachment = ({
  attachment,
  isUploading = false,
  onRemove,
  showRemoveButton = false,
  nameTextColor = "text-muted-foreground",
}: {
  attachment: Attachment;
  isUploading?: boolean;
  onRemove?: () => void;
  showRemoveButton?: boolean;
  nameTextColor?: string;
}) => {
  const { name, url, contentType } = attachment;
  const isImage = contentType?.startsWith("image");
  const isPDF = contentType === "application/pdf";

  return (
    <div className="flex flex-col gap-2 relative group">
      <div className="w-20 aspect-video bg-muted rounded-md relative flex flex-col items-center justify-center overflow-hidden">
        {contentType ? (
          isImage ? (
            // NOTE: it is recommended to use next/image for images
            // eslint-disable-next-line @next/next/no-img-element
            <img
              key={url}
              src={url}
              alt={name ?? "An image attachment"}
              className="size-full object-cover rounded-md"
            />
          ) : isPDF ? (
            <svg className="w-8 h-8 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          )
        ) : (
          <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
          </svg>
        )}

        {isUploading && (
          <div className="animate-spin absolute text-zinc-500">
            <LoaderIcon />
          </div>
        )}

        {showRemoveButton && onRemove && (
          <button
            type="button"
            onClick={onRemove}
            className="absolute top-0 -right-1 bg-destructive hover:bg-destructive/80 text-destructive-foreground rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity shadow-sm z-[1000]"
            aria-label={`Remover ${name}`}
          >
            <TrashIcon size={12} />
          </button>
        )}
      </div>
      <div className={cn("text-xs max-w-20 truncate text-center", nameTextColor)}>{name}</div>
    </div>
  );
};
