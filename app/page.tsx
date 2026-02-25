"use client";

import { FormEvent, useEffect, useState } from "react";

type ImageType = "all" | "flat" | "pano";

type Snapshot = {
  id: string;
  captured_at: string | null;
  lng: number | null;
  lat: number | null;
  camera_type: string | null;
  thumb_url_source: string;
  stored_filename: string;
  stored_url: string;
  ingested_at: string;
};

type IngestResult = {
  fetched: number;
  ingested: number;
  skipped_existing: number;
  failed: number;
};

const INITIAL_FORM = {
  west: "-122.46",
  south: "37.74",
  east: "-122.38",
  north: "37.82",
  limit: "100",
  image_type: "all" as ImageType,
};

export default function Page() {
  const [formValues, setFormValues] = useState(INITIAL_FORM);
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoadingSnapshots, setIsLoadingSnapshots] = useState(false);
  const [isIngesting, setIsIngesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ingestResult, setIngestResult] = useState<IngestResult | null>(null);

  const loadSnapshots = async () => {
    setIsLoadingSnapshots(true);
    setError(null);

    try {
      const response = await fetch("/api/mapillary/snapshots?limit=120&offset=0", {
        cache: "no-store",
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Failed to load snapshots.");
      }

      setTotal(typeof payload.total === "number" ? payload.total : 0);
      setSnapshots(Array.isArray(payload.items) ? payload.items : []);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong while loading snapshots.";
      setError(message);
    } finally {
      setIsLoadingSnapshots(false);
    }
  };

  useEffect(() => {
    void loadSnapshots();
  }, []);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIngestResult(null);

    const west = Number.parseFloat(formValues.west);
    const south = Number.parseFloat(formValues.south);
    const east = Number.parseFloat(formValues.east);
    const north = Number.parseFloat(formValues.north);
    const limit = Number.parseInt(formValues.limit, 10);

    if ([west, south, east, north].some((value) => Number.isNaN(value))) {
      setError("All bbox values must be valid numbers.");
      return;
    }

    if (Number.isNaN(limit) || limit < 1) {
      setError("Limit must be a positive integer.");
      return;
    }

    setIsIngesting(true);
    try {
      const response = await fetch("/api/mapillary/ingest", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bbox: {
            west,
            south,
            east,
            north,
          },
          limit,
          image_type: formValues.image_type,
        }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Ingestion failed.");
      }

      setIngestResult({
        fetched: payload.fetched,
        ingested: payload.ingested,
        skipped_existing: payload.skipped_existing,
        failed: payload.failed,
      });
      await loadSnapshots();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong during ingestion.";
      setError(message);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-10">
      <section className="rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-semibold">Mapillary Snapshot Ingestion</h1>
        <p className="mt-2 text-sm text-neutral-600">
          Ingest Mapillary 1024px street-level snapshots for training workflows and browse the
          stored dataset below.
        </p>

        <form className="mt-6 grid gap-4 md:grid-cols-3" onSubmit={handleSubmit}>
          <label className="flex flex-col gap-1 text-sm">
            West
            <input
              className="rounded-md border border-neutral-300 px-3 py-2"
              type="number"
              step="any"
              value={formValues.west}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  west: event.target.value,
                }))
              }
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            South
            <input
              className="rounded-md border border-neutral-300 px-3 py-2"
              type="number"
              step="any"
              value={formValues.south}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  south: event.target.value,
                }))
              }
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            East
            <input
              className="rounded-md border border-neutral-300 px-3 py-2"
              type="number"
              step="any"
              value={formValues.east}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  east: event.target.value,
                }))
              }
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            North
            <input
              className="rounded-md border border-neutral-300 px-3 py-2"
              type="number"
              step="any"
              value={formValues.north}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  north: event.target.value,
                }))
              }
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            Limit
            <input
              className="rounded-md border border-neutral-300 px-3 py-2"
              type="number"
              min={1}
              max={500}
              value={formValues.limit}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  limit: event.target.value,
                }))
              }
            />
          </label>

          <label className="flex flex-col gap-1 text-sm">
            Image Type
            <select
              className="rounded-md border border-neutral-300 px-3 py-2"
              value={formValues.image_type}
              onChange={(event) =>
                setFormValues((current) => ({
                  ...current,
                  image_type: event.target.value as ImageType,
                }))
              }
            >
              <option value="all">all</option>
              <option value="flat">flat</option>
              <option value="pano">pano</option>
            </select>
          </label>

          <div className="md:col-span-3">
            <button
              className="rounded-md bg-black px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isIngesting}
              type="submit"
            >
              {isIngesting ? "Ingesting..." : "Ingest Snapshots"}
            </button>
          </div>
        </form>

        {ingestResult && (
          <div className="mt-4 rounded-md bg-neutral-100 p-3 text-sm">
            <p>Fetched: {ingestResult.fetched}</p>
            <p>Ingested: {ingestResult.ingested}</p>
            <p>Skipped Existing: {ingestResult.skipped_existing}</p>
            <p>Failed: {ingestResult.failed}</p>
          </div>
        )}

        {error && <p className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      </section>

      <section>
        <div className="mb-4 flex items-center justify-between gap-3">
          <h2 className="text-xl font-semibold">Stored Snapshots</h2>
          <p className="text-sm text-neutral-600">Total: {total}</p>
        </div>

        {isLoadingSnapshots ? (
          <p className="text-sm text-neutral-600">Loading snapshots...</p>
        ) : snapshots.length === 0 ? (
          <p className="text-sm text-neutral-600">
            No snapshots stored yet. Run an ingest request to populate the dataset.
          </p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {snapshots.map((snapshot) => {
              const capturedDate = snapshot.captured_at ? new Date(snapshot.captured_at) : null;
              const capturedAtLabel =
                capturedDate && !Number.isNaN(capturedDate.getTime())
                  ? capturedDate.toLocaleString()
                  : "Unknown";
              const lngLabel =
                typeof snapshot.lng === "number" ? snapshot.lng.toFixed(6) : "Unknown";
              const latLabel =
                typeof snapshot.lat === "number" ? snapshot.lat.toFixed(6) : "Unknown";

              return (
                <article
                  key={snapshot.id}
                  className="overflow-hidden rounded-xl border border-neutral-200 bg-white shadow-sm"
                >
                  <img
                    alt={`Mapillary snapshot ${snapshot.id}`}
                    className="h-48 w-full object-cover"
                    loading="lazy"
                    src={snapshot.stored_url}
                  />
                  <div className="flex flex-col gap-1 p-3 text-sm">
                    <p className="font-medium">ID: {snapshot.id}</p>
                    <p>Captured: {capturedAtLabel}</p>
                    <p>Coords: {lngLabel}, {latLabel}</p>
                    <p>Camera: {snapshot.camera_type ?? "Unknown"}</p>
                    <a
                      className="mt-1 text-blue-600 underline"
                      href={snapshot.stored_url}
                      rel="noreferrer"
                      target="_blank"
                    >
                      Open image
                    </a>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </section>
    </main>
  );
}
