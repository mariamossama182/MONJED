import { useState } from "react";
import { Link } from "react-router-dom";
import { MapPin, Phone, ArrowRight, CheckCircle2 } from "lucide-react";
import { createAssistanceRequest, ApiError } from "../lib/api.js";
import { useAuth } from "../lib/auth.jsx";
import TextField from "../components/ui/TextField.jsx";

const NEEDS = [
  { id: "other", label: "Need help", api: "other" },
  { id: "transportation", label: "No transport", api: "transportation" },
  { id: "mobility_assistance", label: "Mobility assistance", api: "mobility_assistance" },
];

export default function HelpPage() {
  const { session } = useAuth();
  const [need, setNeed] = useState("other");
  const [location, setLocation] = useState(() => {
    if (!session) return "";
    return [session.zone, session.country].filter(Boolean).join(", ");
  });
  const [phone, setPhone] = useState(session?.phone || "");
  const [details, setDetails] = useState("");
  const [people, setPeople] = useState("1");
  const [saved, setSaved] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    const zone_id = session?.zone_id || session?.countryCode || "KE";
    const selected = NEEDS.find((n) => n.id === need) || NEEDS[0];
    try {
      const record = await createAssistanceRequest({
        zone_id,
        location: location.trim() || zone_id,
        hazard: "flood",
        request_type: selected.api,
        priority: "high",
        description:
          details.trim() ||
          `${selected.label}. Phone: ${phone.trim() || "n/a"}. People: ${people}.`,
      });
      setSaved(record);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create help request.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-5 sm:px-8 py-10 pb-16">
      <h1 className="font-display text-3xl sm:text-4xl font-bold leading-tight">
        Request help
      </h1>
      <p className="mt-3 text-sm text-slate">
        Signed in as {session?.name}. Request is stored on the MONJED assistance API
        until ops matches a volunteer.
      </p>

      {error && (
        <p className="mt-4 text-sm text-crimson border border-crimson/30 bg-crimson/10 rounded-md px-3 py-2">
          {error}
        </p>
      )}

      {saved ? (
        <div className="mt-8 rounded-xl border border-teal/30 bg-teal/10 p-6 sm:p-8">
          <div className="flex items-center gap-2 text-teal">
            <CheckCircle2 size={20} />
            <p className="font-mono text-[10px] tracking-widest">
              QUEUED · {saved.request_id} · {saved.status}
            </p>
          </div>
          <p className="mt-4 text-sm text-mist">{saved.description}</p>
          <p className="mt-2 text-xs text-slate">{saved.location} · zone {saved.zone_id}</p>
          <Link to="/map" className="mt-6 inline-flex items-center gap-1.5 text-sm text-amber hover:underline">
            Back to map <ArrowRight size={14} />
          </Link>
        </div>
      ) : (
        <form onSubmit={onSubmit} className="mt-8 space-y-5">
          <div className="flex flex-wrap gap-2">
            {NEEDS.map((n) => (
              <button
                key={n.id}
                type="button"
                onClick={() => setNeed(n.id)}
                className={`rounded-md border px-3 py-2 text-sm ${
                  need === n.id ? "border-amber/50 bg-amber/10" : "border-line"
                }`}
              >
                {n.label}
              </button>
            ))}
          </div>
          <TextField
            label="Where are you"
            icon={MapPin}
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            required
            minLength={2}
          />
          <TextField
            label="How many people"
            type="number"
            min="1"
            max="50"
            value={people}
            onChange={(e) => setPeople(e.target.value)}
            required
          />
          <TextField
            label="Phone"
            icon={Phone}
            type="tel"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
            minLength={7}
          />
          <label className="block">
            <span className="block text-xs font-mono tracking-wide text-slate mb-1.5">Details</span>
            <textarea
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-line bg-panel px-3 py-2 text-sm"
              placeholder="What do you need?"
            />
          </label>
          <button
            type="submit"
            disabled={busy}
            className="w-full rounded-md bg-amber py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
          >
            {busy ? "Sending…" : "Submit help request"}
          </button>
        </form>
      )}
    </div>
  );
}
