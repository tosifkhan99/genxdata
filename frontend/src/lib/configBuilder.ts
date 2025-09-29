import type { FormData } from "@/components/ConfigForm/ConfigForm";

const writerTypeMap: Record<string, string> = {
  CSV: "csv",
  Json: "json",
  JSON: "json",
  Excel: "excel",
  Parquet: "parquet",
  Feather: "feather",
};

export const buildCoreConfig = (form: FormData) => {
  const writerType = writerTypeMap[form.file_writer_type] || "csv";
  const safeName = (form.metadata.name || "data")
    .replace(/[^a-zA-Z0-9_-]/g, "_")
    .toLowerCase();

  const configs = form.configs
    .filter((c) => c?.names?.[0] && c.strategy?.name)
    .map((c) => ({
      column_names: c.names,
      strategy: {
        name: c.strategy.name,
        params: c.strategy.params || {},
      },
      ...(c.mask && c.mask.trim() ? { mask: c.mask } : {}),
    }));

  return {
    metadata: form.metadata,
    column_name: form.column_name.filter((n) => n && n.trim() !== ""),
    num_of_rows: form.num_of_rows,
    shuffle: form.shuffle,
    file_writer: {
      type: writerType,
      params: {
        output_path: `output/${safeName}.${writerType === "excel" ? "xlsx" : writerType}`,
      },
    },
    configs,
  } as const;
};

export type CoreConfig = ReturnType<typeof buildCoreConfig>;
