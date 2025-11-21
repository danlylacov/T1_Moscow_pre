"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import type { StackItem } from "./stack-card";

interface EditableStackItem extends StackItem {
  enabled: boolean;
  versions: string[];
}

interface EditStackDialogProps {
  items: EditableStackItem[];
  onChange: (items: EditableStackItem[]) => void;
  disabled?: boolean;
}

export function EditStackDialog({
  items,
  onChange,
  disabled,
}: EditStackDialogProps) {
  const [open, setOpen] = React.useState(false);
  const [localItems, setLocalItems] = React.useState<EditableStackItem[]>(items);

  React.useEffect(() => {
    setLocalItems(items);
  }, [items, open]);

  const handleToggle = (id: string, enabled: boolean) => {
    setLocalItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, enabled } : item))
    );
  };

  const handleVersionChange = (id: string, version: string) => {
    setLocalItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, value: version } : item
      )
    );
  };

  const handleSave = () => {
    onChange(localItems);
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button
          variant="secondary"
          size="sm"
          disabled={disabled}
        >
          Edit Stack
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Edit detected stack</DialogTitle>
          <DialogDescription>
            Adjust technologies and versions before generating the pipeline.
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3 pt-1 text-xs">
          {localItems.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between gap-3 rounded-md border border-slate-800 bg-slate-950/80 px-3 py-2"
            >
              <div className="flex flex-1 items-center gap-3">
                <Checkbox
                  checked={item.enabled}
                  onChange={(e) => handleToggle(item.id, e.target.checked)}
                  aria-label={item.label}
                />
                <div>
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium text-slate-100">
                      {item.label}
                    </span>
                    <Badge variant="outline" className="text-[10px]">
                      {item.type}
                    </Badge>
                  </div>
                  <p className="mt-0.5 text-[11px] text-slate-500">
                    Current: {item.value}
                  </p>
                </div>
              </div>
              <div className="w-32">
                {item.versions.length > 0 && (
                  <Select
                    value={item.value}
                    onChange={(e) =>
                      handleVersionChange(item.id, e.target.value)
                    }
                  >
                    {item.versions.map((version) => (
                      <option key={version} value={version}>
                        {version}
                      </option>
                    ))}
                  </Select>
                )}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setOpen(false)}
          >
            Cancel
          </Button>
          <Button size="sm" onClick={handleSave}>
            Save changes
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}


