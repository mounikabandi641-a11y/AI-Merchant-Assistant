import { useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  ArrowDownRight,
  ArrowRight,
  ArrowUpRight,
  Bell,
  Bot,
  Check,
  ChevronDown,
  CircleHelp,
  Clock3,
  CreditCard,
  FileWarning,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageCircle,
  Search,
  Send,
  ShieldAlert,
  ShieldCheck,
  Sparkles,
  Trash2,
  User,
  X,
} from 'lucide-react';
import { api } from './services/api.js';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'transactions', label: 'Transactions', icon: CreditCard },
  { id: 'disputes', label: 'Dispute Center', icon: FileWarning },
  { id: 'risk', label: 'Risk Analysis', icon: Activity },
  { id: 'assistant', label: 'AI Assistant', icon: MessageCircle },
];

const disputeTypes = [
  ['PAYMENT_FAILED_DEBITED', 'Payment failed, debited'],
  ['DUPLICATE_TRANSACTION', 'Duplicate transaction'],
  ['PAYMENT_NOT_RECEIVED', 'Payment not received'],
  ['REFUND_ISSUE', 'Refund issue'],
  ['UNKNOWN_TRANSACTION', 'Unknown transaction'],
  ['OTHER', 'Other'],
];

const titleByPage = {
  dashboard: 'Dashboard',
  transactions: 'Transactions',
  'transaction-details': 'Transaction details',
  disputes: 'Dispute center',
  risk: 'Risk analysis',
  assistant: 'AI Assistant',
};

function formatAmount(value) {
  return Number(value || 0).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? String(value)
    : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function statusTone(value) {
  const status = String(value || '').toLowerCase();
  if (['completed', 'success', 'succeeded', 'resolved', 'closed'].includes(status)) return 'good';
  if (['failed', 'rejected', 'high', 'elevated'].includes(status)) return 'bad';
  if (['open', 'pending', 'medium', 'in_review'].includes(status)) return 'warning';
  return 'neutral';
}

function riskTone(value) {
  const level = String(value || 'unknown').toLowerCase();
  if (['high', 'elevated', 'critical'].some((term) => level.includes(term))) return 'bad';
  if (['medium', 'moderate'].some((term) => level.includes(term))) return 'warning';
  if (['low', 'minimal'].some((term) => level.includes(term))) return 'good';
  return 'neutral';
}

function Badge({ children, tone = 'neutral', dot = false }) {
  return <span className={`badge badge-${tone}`}>{dot && <i />}{children}</span>;
}

function PageHeading({ eyebrow, title, detail, action }) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1>{title}</h1>
        {detail && <p className="page-detail">{detail}</p>}
      </div>
      {action}
    </div>
  );
}

function MetricCard({ label, value, footnote, icon: Icon, color, trend }) {
  return (
    <article className="metric-card">
      <div className={`metric-icon metric-${color}`}><Icon size={18} strokeWidth={1.8} /></div>
      <div className="metric-trend">{trend}</div>
      <p className="metric-label">{label}</p>
      <strong className="metric-value">{value}</strong>
      <p className="metric-footnote">{footnote}</p>
    </article>
  );
}

function EmptyState({ icon: Icon = CircleHelp, title, detail }) {
  return (
    <div className="empty-state">
      <span className="empty-icon"><Icon size={20} /></span>
      <strong>{title}</strong>
      <p>{detail}</p>
    </div>
  );
}

function TransactionTable({ transactions, onSelect, compact = false, showSearch = false, riskOnly = false }) {
  const [query, setQuery] = useState('');
  const visibleTransactions = useMemo(() => {
    const filtered = riskOnly
      ? transactions.filter((item) => ['high', 'elevated', 'critical', 'medium'].includes(String(item.fraud_risk_label).toLowerCase()))
      : transactions;
    const search = query.trim().toLowerCase();
    return search ? filtered.filter((item) => String(item.transaction_id).toLowerCase().includes(search)) : filtered;
  }, [transactions, query, riskOnly]);

  return (
    <>
      {showSearch && (
        <label className="search-box">
          <Search size={16} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search transaction ID" />
          {query && <button type="button" className="clear-search" aria-label="Clear search" onClick={() => setQuery('')}><X size={14} /></button>}
        </label>
      )}
      {visibleTransactions.length === 0 ? (
        <EmptyState icon={Search} title={query ? 'No matching transactions' : 'No transactions yet'} detail={query ? 'Try another transaction ID.' : 'Transactions from the connected database will appear here.'} />
      ) : (
        <div className="table-scroll">
          <table className={compact ? 'data-table compact-table' : 'data-table'}>
            <thead>
              <tr>
                <th>Transaction</th>
                <th>Amount</th>
                <th>Payment status</th>
                {!compact && <th>Method</th>}
                {!compact && <th>Device / location</th>}
                <th>Risk</th>
                <th aria-label="Open details" />
              </tr>
            </thead>
            <tbody>
              {visibleTransactions.map((transaction) => (
                <tr key={transaction.transaction_id} onClick={() => onSelect(transaction)} tabIndex={0} onKeyDown={(event) => event.key === 'Enter' && onSelect(transaction)}>
                  <td><span className="table-id">{transaction.transaction_id}</span><small>{formatDate(transaction.transaction_time)}</small></td>
                  <td className="amount-cell">{formatAmount(transaction.amount)}</td>
                  <td><Badge tone={statusTone(transaction.payment_status)} dot>{transaction.payment_status}</Badge></td>
                  {!compact && <td>{transaction.payment_method || '—'}</td>}
                  {!compact && <td><span>{transaction.device_type || '—'}</span><small>{transaction.location || '—'}</small></td>}
                  <td><Badge tone={riskTone(transaction.fraud_risk_label)} dot>{transaction.fraud_risk_label || 'Unknown'}</Badge></td>
                  <td><button type="button" className="icon-button row-open" aria-label={`Open ${transaction.transaction_id}`} onClick={(event) => { event.stopPropagation(); onSelect(transaction); }}><ArrowRight size={16} /></button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

function DisputeList({ disputes, onOpen }) {
  if (!disputes.length) {
    return <EmptyState icon={FileWarning} title="No disputes on file" detail="New cases submitted for review will appear here." />;
  }
  return (
    <div className="dispute-list">
      {disputes.map((dispute) => (
        <article className="dispute-row" key={dispute.dispute_id}>
          <div className="dispute-mark"><FileWarning size={17} /></div>
          <div className="dispute-content">
            <div className="dispute-title-line"><strong>{dispute.dispute_type?.replaceAll('_', ' ') || 'Dispute'}</strong><Badge tone={statusTone(dispute.status)} dot>{dispute.status}</Badge></div>
            <p>{dispute.description || 'No customer description provided.'}</p>
            <div className="dispute-meta"><span>{dispute.transaction_id}</span><span>{formatDate(dispute.created_at)}</span></div>
            {dispute.recommended_action && <div className="action-note"><ShieldCheck size={14} /><span>{dispute.recommended_action}</span></div>}
          </div>
          {onOpen && <button type="button" className="text-button dispute-open" onClick={() => onOpen(dispute)}>View <ArrowRight size={14} /></button>}
        </article>
      ))}
    </div>
  );
}

function Dashboard({ transactions, disputes, onSelectTransaction, onNavigate, onOpenDispute }) {
  const successful = transactions.filter((item) => ['completed', 'success', 'succeeded'].includes(String(item.payment_status).toLowerCase())).length;
  const failed = transactions.filter((item) => ['failed', 'rejected'].includes(String(item.payment_status).toLowerCase())).length;
  const openDisputes = disputes.filter((item) => ['open', 'pending', 'in_review'].includes(String(item.status).toLowerCase())).length;
  const elevated = transactions.filter((item) => ['high', 'elevated', 'critical', 'medium'].includes(String(item.fraud_risk_label).toLowerCase())).length;
  const riskCount = transactions.filter((item) => ['high', 'elevated', 'critical'].includes(String(item.fraud_risk_label).toLowerCase())).length;
  const riskShare = transactions.length ? Math.round((riskCount / transactions.length) * 100) : 0;

  return (
    <>
      <PageHeading eyebrow="MERCHANT OVERVIEW" title="Good morning" detail="A clear view of your payments, risk signals, and cases that need attention." action={<button className="button button-secondary" onClick={() => onNavigate('transactions')}><CreditCard size={16} /> All transactions</button>} />
      <section className="metric-grid">
        <MetricCard label="Total transactions" value={transactions.length.toLocaleString()} footnote="Records in connected database" icon={CreditCard} color="mint" trend={<ArrowUpRight size={15} />} />
        <MetricCard label="Successful" value={successful.toLocaleString()} footnote="Completed payments" icon={Check} color="green" trend={<span className="trend-label">Settled</span>} />
        <MetricCard label="Failed" value={failed.toLocaleString()} footnote="Requires monitoring" icon={ArrowDownRight} color="coral" trend={<span className="trend-label">Payments</span>} />
        <MetricCard label="Open disputes" value={openDisputes.toLocaleString()} footnote="Awaiting merchant review" icon={FileWarning} color="amber" trend={<span className="trend-label">Cases</span>} />
        <MetricCard label="Elevated risk" value={elevated.toLocaleString()} footnote="Medium or high indicators" icon={ShieldAlert} color="blue" trend={<span className="trend-label">Signals</span>} />
      </section>

      <section className="dashboard-grid">
        <article className="panel transactions-panel">
          <div className="panel-heading"><div><p className="eyebrow">PAYMENT ACTIVITY</p><h2>Recent transactions</h2></div><button className="text-button" onClick={() => onNavigate('transactions')}>View all <ArrowRight size={15} /></button></div>
          <TransactionTable transactions={[...transactions].slice(-5).reverse()} onSelect={onSelectTransaction} compact />
        </article>
        <article className="panel pulse-panel">
          <div className="panel-heading"><div><p className="eyebrow">SIGNAL MONITOR</p><h2>Risk snapshot</h2></div><span className="signal-icon"><Activity size={16} /></span></div>
          <div className="risk-score-line"><div><strong>{riskShare}%</strong><span>high-risk share</span></div><Badge tone={riskCount ? 'warning' : 'good'} dot>{riskCount ? 'Review signals' : 'No high-risk signals'}</Badge></div>
          <div className="risk-meter"><span style={{ width: `${riskShare}%` }} /></div>
          <div className="risk-breakdown">
            <div><span className="risk-key risk-high" />High risk <strong>{riskCount}</strong></div>
            <div><span className="risk-key risk-medium" />Medium risk <strong>{transactions.filter((item) => String(item.fraud_risk_label).toLowerCase() === 'medium').length}</strong></div>
            <div><span className="risk-key risk-low" />Low risk <strong>{transactions.filter((item) => String(item.fraud_risk_label).toLowerCase() === 'low').length}</strong></div>
          </div>
          <button className="panel-link" onClick={() => onNavigate('risk')}>Review risk analysis <ArrowRight size={15} /></button>
        </article>
        <article className="panel recent-disputes-panel">
          <div className="panel-heading"><div><p className="eyebrow">CASE MANAGEMENT</p><h2>Recent disputes</h2></div><button className="text-button" onClick={() => onNavigate('disputes')}>Open center <ArrowRight size={15} /></button></div>
          <DisputeList disputes={[...disputes].reverse().slice(0, 3)} onOpen={onOpenDispute} />
        </article>
      </section>
    </>
  );
}

function TransactionDetails({ transaction, riskResult, analyzing, onAnalyze, onBack, onAskAssistant }) {
  const fields = [
    ['Payment status', transaction.payment_status],
    ['Payment method', transaction.payment_method],
    ['Device type', transaction.device_type],
    ['Location', transaction.location],
    ['Failed attempts', transaction.failed_attempts],
    ['Transaction frequency', transaction.transaction_frequency],
    ['Previous chargebacks', transaction.previous_chargebacks],
  ];
  return (
    <>
      <PageHeading eyebrow="TRANSACTION RECORD" title={transaction.transaction_id} detail="Review the transaction facts and request a model risk estimate." action={<div className="page-actions"><button className="button button-secondary" onClick={onBack}><ArrowRight className="back-arrow" size={16} /> Back to transactions</button><button className="button button-primary" onClick={onAskAssistant}><MessageCircle size={16} /> Ask Assistant</button></div>} />
      <section className="detail-layout">
        <article className="panel detail-panel">
          <div className="detail-amount"><span>Transaction amount</span><strong>{formatAmount(transaction.amount)}</strong><Badge tone={statusTone(transaction.payment_status)} dot>{transaction.payment_status}</Badge></div>
          <div className="detail-grid">{fields.map(([label, value]) => <div className="detail-field" key={label}><span>{label}</span><strong>{value ?? '—'}</strong></div>)}</div>
          <div className="detail-note"><Clock3 size={16} /><span>Created {formatDate(transaction.transaction_time)} · Merchant {transaction.merchant_id || '—'}</span></div>
        </article>
        <aside className="panel analyze-panel">
          <div className="panel-heading"><div><p className="eyebrow">MODEL ASSISTANCE</p><h2>Risk assessment</h2></div><span className="assessment-icon"><Sparkles size={18} /></span></div>
          {!riskResult ? <div className="assessment-intro"><div className="shield-art"><ShieldCheck size={26} /></div><p>Run the trained model against the available transaction attributes to get a risk estimate.</p><small>This signal supports review; it is not a finding of fraud.</small></div> : (
            <div className="prediction-result">
              <div className="prediction-top"><span>Model estimate</span><Badge tone={riskTone(riskResult.risk_category)} dot>{riskResult.risk_category}</Badge></div>
              <strong className="prediction-score">{Number(riskResult.risk_score) <= 1 ? `${Math.round(Number(riskResult.risk_score) * 100)}%` : `${Number(riskResult.risk_score).toFixed(1)}%`}</strong>
              <p>{riskResult.message}</p>
              <small>Use this estimate as a review indicator, not a final decision.</small>
            </div>
          )}
          <button className="button button-primary button-full" onClick={() => onAnalyze(transaction)} disabled={analyzing}>{analyzing ? <span className="spinner" /> : <Sparkles size={16} />}{analyzing ? 'Analyzing…' : 'Analyze Risk'}</button>
        </aside>
      </section>
    </>
  );
}

function DisputeCenter({ disputes, transactions, onResolved, initialDispute }) {
  const [transactionId, setTransactionId] = useState('');
  const [disputeType, setDisputeType] = useState(disputeTypes[0][0]);
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [expanded, setExpanded] = useState(initialDispute?.dispute_id || '');

  useEffect(() => {
    if (initialDispute) {
      setTransactionId(initialDispute.transaction_id || '');
      setExpanded(initialDispute.dispute_id || '');
    }
  }, [initialDispute]);

  async function submit(event) {
    event.preventDefault();
    setError('');
    setResult(null);
    setSubmitting(true);
    try {
      const resolution = await api.resolveDispute({
        transaction_id: transactionId.trim(),
        dispute_type: disputeType,
        description: description.trim(),
      });
      setResult(resolution);
      setExpanded(resolution.dispute_id);
      setDescription('');
      await onResolved();
    } catch (requestError) {
      setError(requestError.message || 'Could not resolve this dispute.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <PageHeading eyebrow="MERCHANT REVIEW WORKFLOW" title="Dispute center" detail="Organize reported payment issues and prepare a safe next step for merchant review." />
      <section className="dispute-workspace">
        <article className="panel dispute-form-panel">
          <div className="panel-heading"><div><p className="eyebrow">NEW CASE</p><h2>Analyze a dispute</h2></div><span className="form-mark"><FileWarning size={17} /></span></div>
          <form className="dispute-form" onSubmit={submit}>
            <label>Transaction ID
              <input list="transaction-options" required value={transactionId} onChange={(event) => setTransactionId(event.target.value)} placeholder="e.g. TXN-1042" />
              <datalist id="transaction-options">{transactions.map((item) => <option key={item.transaction_id} value={item.transaction_id} />)}</datalist>
            </label>
            <label>Dispute type
              <select value={disputeType} onChange={(event) => setDisputeType(event.target.value)}>{disputeTypes.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select>
            </label>
            <label>Description
              <textarea required rows="4" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="Summarize the customer's reported issue" /></label>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="button button-primary button-full" disabled={submitting}>{submitting ? <span className="spinner" /> : <Sparkles size={16} />}{submitting ? 'Analyzing…' : 'Resolve / Analyze'}</button>
            <p className="form-footnote"><ShieldCheck size={14} />Recommendations require merchant review. No refund or reversal is initiated.</p>
          </form>
          {result && <div className="resolution-result" role="status"><div className="resolution-title"><Badge tone="warning" dot>{result.status}</Badge><span>{result.dispute_category.replaceAll('_', ' ')}</span></div><p>{result.explanation}</p><strong>Recommended next step</strong><p>{result.recommended_action}</p></div>}
        </article>
        <article className="panel dispute-records-panel">
          <div className="panel-heading"><div><p className="eyebrow">CASE QUEUE</p><h2>Existing disputes <span className="count-pill">{disputes.length}</span></h2></div><span className="case-icon"><FileWarning size={17} /></span></div>
          {!disputes.length ? <EmptyState icon={FileWarning} title="The queue is clear" detail="Resolved and active cases from the API will show here." /> : (
            <div className="case-queue">
              {[...disputes].reverse().map((dispute) => (
                <article className={`case-card ${expanded === dispute.dispute_id ? 'case-expanded' : ''}`} key={dispute.dispute_id}>
                  <button className="case-toggle" onClick={() => setExpanded(expanded === dispute.dispute_id ? '' : dispute.dispute_id)}>
                    <span><strong>{dispute.dispute_type?.replaceAll('_', ' ')}</strong><small>{dispute.transaction_id} · {formatDate(dispute.created_at)}</small></span>
                    <span className="case-toggle-end"><Badge tone={statusTone(dispute.status)} dot>{dispute.status}</Badge><ChevronDown size={16} /></span>
                  </button>
                  {expanded === dispute.dispute_id && <div className="case-details"><p className="case-label">Reported issue / explanation</p><p>{dispute.description || 'No description was provided.'}</p><p className="case-label">Recommended action</p><p>{dispute.recommended_action || 'Manual review required.'}</p><button type="button" className="text-button" onClick={async () => { try { const fresh = await api.getDispute(dispute.dispute_id); setExpanded(fresh.dispute_id); } catch (requestError) { setError(requestError.message); } }}>Refresh case details <ArrowRight size={14} /></button></div>}
                </article>
              ))}
            </div>
          )}
        </article>
      </section>
    </>
  );
}

const assistantWelcome = {
  id: 'assistant-welcome',
  role: 'assistant',
  content: 'Hello. I can explain transaction records, summarize model risk results, and share dispute review guidance using information in this application. A merchant makes every final decision.',
  sources: [],
};

const assistantQuickQuestions = [
  'Why is this transaction risky?',
  'How do I handle a duplicate dispute?',
  'What should I check before resolving a dispute?',
  'Explain payment failed but debited.',
];

function AssistantChat({ transactions, initialTransactionId, onSelectTransaction }) {
  const [transactionId, setTransactionId] = useState(initialTransactionId || '');
  const [messages, setMessages] = useState([assistantWelcome]);
  const [draft, setDraft] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (initialTransactionId) setTransactionId(initialTransactionId);
  }, [initialTransactionId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, sending]);

  async function sendMessage(message = draft) {
    const content = message.trim();
    if (!content || sending) return;
    setDraft('');
    setError('');
    setMessages((current) => [...current, { id: `${Date.now()}-user`, role: 'user', content }]);
    setSending(true);
    const lowerContent = content.toLowerCase();
    const disputeQuestion = /dispute|duplicate|refund|payment failed|debited|not received|before resolving/.test(lowerContent);
    const containsTransactionId = /\b[A-Za-z][A-Za-z0-9_-]*\d[A-Za-z0-9_-]*\b/.test(content);
    const contextualId = transactionId && !disputeQuestion && !containsTransactionId ? transactionId : undefined;
    try {
      const response = await api.chatAssistant({ message: content, transaction_id: contextualId });
      setMessages((current) => [...current, {
        id: `${Date.now()}-assistant`,
        role: 'assistant',
        content: response.answer,
        relatedTransactionId: response.related_transaction_id,
        sources: response.sources || [],
      }]);
    } catch (requestError) {
      setError(requestError.message || 'The assistant could not reach the application data.');
    } finally {
      setSending(false);
    }
  }

  function clearChat() {
    setMessages([assistantWelcome]);
    setDraft('');
    setError('');
  }

  return (
    <section className="assistant-workspace">
      <article className="panel assistant-chat-panel">
        <div className="assistant-toolbar">
          <span className="assistant-avatar"><Bot size={19} /></span>
          <div className="assistant-title"><strong>AI Merchant Assistant</strong><small>Local guidance · connected application data</small></div>
          <span className="assistant-mode"><i /> LOCAL</span>
          <button type="button" className="button button-secondary clear-chat" onClick={clearChat}><Trash2 size={14} /> Clear chat</button>
        </div>
        <div className="assistant-context">
          <label htmlFor="assistant-transaction-context">Transaction context</label>
          <select id="assistant-transaction-context" value={transactionId} onChange={(event) => setTransactionId(event.target.value)}>
            <option value="">No transaction selected</option>
            {transactions.map((transaction) => <option key={transaction.transaction_id} value={transaction.transaction_id}>{transaction.transaction_id}</option>)}
          </select>
          <span>Context is used for transaction questions only.</span>
        </div>
        <div className="assistant-chat-history" role="log" aria-live="polite" aria-label="Assistant conversation">
          {messages.map((item) => (
            <div className={`chat-message chat-${item.role}`} key={item.id}>
              <span className="chat-avatar">{item.role === 'assistant' ? <Bot size={15} /> : <User size={15} />}</span>
              <div className="chat-message-body">
                <div className="chat-speaker">{item.role === 'assistant' ? 'AI Merchant Assistant' : 'You'}</div>
                <p>{item.content}</p>
                {item.relatedTransactionId && <button type="button" className="chat-related-link" onClick={() => { const transaction = transactions.find((entry) => entry.transaction_id === item.relatedTransactionId); if (transaction) onSelectTransaction(transaction); }}>Related transaction: {item.relatedTransactionId} <ArrowRight size={13} /></button>}
                {item.sources?.length > 0 && <div className="chat-sources"><span>Sources</span>{item.sources.map((source) => <span className="source-tag" key={source}>{source}</span>)}</div>}
              </div>
            </div>
          ))}
          {sending && <div className="chat-message chat-assistant"><span className="chat-avatar"><Bot size={15} /></span><div className="chat-message-body"><div className="chat-speaker">AI Merchant Assistant</div><p className="assistant-waiting"><span className="spinner" /> Checking application information…</p></div></div>}
          <div ref={chatEndRef} />
        </div>
        {error && <p className="assistant-error" role="alert">{error} Check the local backend connection and try again.</p>}
        <div className="assistant-prompts" aria-label="Example questions">
          <span>TRY ASKING</span>
          {assistantQuickQuestions.map((question) => <button type="button" key={question} onClick={() => sendMessage(question)} disabled={sending}>{question}</button>)}
        </div>
        <form className="assistant-composer" onSubmit={(event) => { event.preventDefault(); sendMessage(); }}>
          <textarea value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); sendMessage(); } }} placeholder="Ask about a transaction or dispute…" aria-label="Message AI Merchant Assistant" rows="2" />
          <button type="submit" className="button button-primary send-button" disabled={sending || !draft.trim()} aria-label="Send message">{sending ? <span className="spinner" /> : <Send size={16} />}<span>Send</span></button>
        </form>
        <p className="assistant-safety-note"><ShieldCheck size={14} />Guidance only. Verify records and make all final decisions as the merchant. No refunds or financial actions are initiated.</p>
      </article>
    </section>
  );
}

function Login({ onLogin }) {
  const [identity, setIdentity] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  function submit(event) {
    event.preventDefault();
    if (!identity.trim() || !password.trim()) {
      setError('Enter a username and password to continue.');
      return;
    }
    onLogin(identity.trim());
  }
  return (
    <main className="login-screen">
      <section className="login-visual">
        <div className="login-brand"><span className="brand-mark"><Activity size={20} /></span><span>AI Merchant<br />Assistant</span></div>
        <div className="login-message"><span className="login-kicker"><i /> MERCHANT OPERATIONS</span><h1>Clarity for every<br /><em>payment moment.</em></h1><p>Bring transactions, risk signals, and dispute workflows into one considered workspace.</p></div>
        <div className="visual-footer"><span>SECURE REVIEW WORKSPACE</span><span>DEMO ENVIRONMENT · SYNTHETIC DATA</span></div>
        <div className="login-orbit orbit-one" /><div className="login-orbit orbit-two" /><div className="login-shape"><div className="shape-ring" /><div className="shape-core"><ShieldCheck size={38} /></div><span className="shape-chip chip-a"><Check size={13} /> Payment verified</span><span className="shape-chip chip-b"><Activity size={13} /> Risk monitored</span></div>
      </section>
      <section className="login-form-side">
        <div className="login-mobile-brand"><span className="brand-mark"><Activity size={19} /></span><strong>AI Merchant Assistant</strong></div>
        <div className="login-form-wrap"><div className="login-heading"><p className="eyebrow">WELCOME BACK</p><h2>Sign in to your workspace</h2><p>Use any username and password for this local demo.</p></div>
          <form className="login-form" onSubmit={submit}>
            <label>Email or username<input autoComplete="username" value={identity} onChange={(event) => setIdentity(event.target.value)} placeholder="merchant@demo.local" /></label>
            <label>Password<input autoComplete="current-password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="Enter a demo password" /></label>
            {error && <p className="form-error" role="alert">{error}</p>}
            <button className="button button-primary button-full login-submit">Continue <ArrowRight size={16} /></button>
          </form>
          <p className="demo-note"><ShieldCheck size={15} />Local demo access only. The password is never sent or stored.</p>
        </div>
        <div className="login-copyright">AI Merchant Assistant <span>·</span> Hackathon demo</div>
      </section>
    </main>
  );
}

export default function App() {
  const [identity, setIdentity] = useState(() => sessionStorage.getItem('merchant-demo-user') || '');
  const [page, setPage] = useState('dashboard');
  const [transactions, setTransactions] = useState([]);
  const [disputes, setDisputes] = useState([]);
  const [selectedTransaction, setSelectedTransaction] = useState(null);
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [riskResult, setRiskResult] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  async function refreshData() {
    setLoading(true);
    setApiError('');
    const [transactionResult, disputeResult] = await Promise.allSettled([api.getTransactions(), api.getDisputes()]);
    if (transactionResult.status === 'fulfilled') setTransactions(transactionResult.value);
    if (disputeResult.status === 'fulfilled') setDisputes(disputeResult.value);
    const failed = [transactionResult, disputeResult].find((item) => item.status === 'rejected');
    if (failed) setApiError(failed.reason?.message || 'Could not load data from the backend.');
    setLoading(false);
  }

  useEffect(() => {
    if (identity) refreshData();
  }, [identity]);

  function navigate(nextPage) {
    setPage(nextPage);
    setSidebarOpen(false);
    if (nextPage !== 'transaction-details') {
      setSelectedDispute(null);
      setRiskResult(null);
    }
  }

  function openTransaction(transaction) {
    setSelectedTransaction(transaction);
    setRiskResult(null);
    setPage('transaction-details');
    setSidebarOpen(false);
  }

  function openDispute(dispute) {
    setSelectedDispute(dispute);
    setPage('disputes');
  }

  async function analyzeRisk(transaction) {
    setAnalyzing(true);
    setApiError('');
    try {
      const prediction = await api.predictRisk({
        amount: transaction.amount,
        payment_method: transaction.payment_method,
        device_type: transaction.device_type,
        failed_attempts: transaction.failed_attempts,
        transaction_frequency: transaction.transaction_frequency,
        customer_age_days: transaction.customer_age_days,
        previous_chargebacks: transaction.previous_chargebacks,
        merchant_id: transaction.merchant_id,
        payment_status: transaction.payment_status,
        location: transaction.location,
        dispute_type: transaction.dispute_type,
      });
      setRiskResult(prediction);
    } catch (requestError) {
      setApiError(requestError.message || 'Risk analysis could not be completed.');
    } finally {
      setAnalyzing(false);
    }
  }

  function login(name) {
    sessionStorage.setItem('merchant-demo-user', name);
    setIdentity(name);
  }

  function logout() {
    sessionStorage.removeItem('merchant-demo-user');
    setIdentity('');
    setPage('dashboard');
  }

  if (!identity) return <Login onLogin={login} />;

  const title = titleByPage[page] || 'Dashboard';
  const initials = identity.slice(0, 1).toUpperCase();

  return (
    <div className="app-shell">
      {sidebarOpen && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setSidebarOpen(false)} />}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand"><span className="brand-mark"><Activity size={19} /></span><span>AI Merchant<br /><strong>Assistant</strong></span></div>
        <div className="workspace-switch"><span className="workspace-avatar">AM</span><span><small>WORKSPACE</small><strong>Merchant demo</strong></span><ChevronDown size={15} /></div>
        <p className="nav-caption">WORKSPACE</p>
        <nav className="primary-nav" aria-label="Main navigation">
          {navItems.map(({ id, label, icon: Icon }) => <button key={id} className={`nav-item ${page === id || (page === 'transaction-details' && id === 'transactions') ? 'nav-active' : ''}`} onClick={() => navigate(id)}><Icon size={18} strokeWidth={1.8} /><span>{label}</span>{id === 'disputes' && disputes.length > 0 && <small className="nav-count">{disputes.length}</small>}</button>)}
        </nav>
        <div className="sidebar-bottom"><div className="sidebar-health"><span className="health-dot" /><span><strong>API connection</strong><small>{apiError ? 'Needs attention' : loading ? 'Checking status…' : 'Dashboard connected'}</small></span></div><button className="nav-item logout-button" onClick={logout}><LogOut size={17} /><span>Sign out</span></button><div className="sidebar-version">AI Merchant Assistant <span>v0.1 demo</span></div></div>
      </aside>

      <main className="main-area">
        <header className="topbar"><div className="topbar-leading"><button className="icon-button menu-button" aria-label="Open navigation" onClick={() => setSidebarOpen(true)}><Menu size={20} /></button><span className="breadcrumb">Workspace <span>/</span> {title}</span></div><div className="topbar-actions"><span className="environment-tag"><i /> DEMO</span><button className="icon-button notification-button" aria-label="Notifications"><Bell size={18} /><i /></button><div className="profile-chip"><span className="profile-avatar">{initials}</span><span>{identity}</span><ChevronDown size={14} /></div></div></header>
        <div className="content-area">
          {apiError && <div className="api-alert" role="alert"><ShieldAlert size={17} /><span><strong>Backend request issue</strong> {apiError} Check that the Java backend is running at localhost:8080.</span><button className="icon-button" onClick={() => setApiError('')} aria-label="Dismiss error"><X size={16} /></button></div>}
          {loading && transactions.length === 0 && disputes.length === 0 ? <div className="loading-panel"><span className="spinner" />Loading merchant data…</div> : null}
          {page === 'dashboard' && <Dashboard transactions={transactions} disputes={disputes} onSelectTransaction={openTransaction} onNavigate={navigate} onOpenDispute={openDispute} />}
          {page === 'transactions' && <><PageHeading eyebrow="PAYMENT LEDGER" title="Transactions" detail="Search, inspect, and analyze transactions from your connected database." action={<button className="button button-secondary" onClick={refreshData}><Activity size={16} /> Refresh data</button>} /><section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">ALL RECORDS</p><h2>Transaction ledger <span className="count-pill">{transactions.length}</span></h2></div><Badge tone="neutral">Synthetic records</Badge></div><TransactionTable transactions={[...transactions].reverse()} onSelect={openTransaction} showSearch /></section></>}
          {page === 'transaction-details' && selectedTransaction && <TransactionDetails transaction={selectedTransaction} riskResult={riskResult} analyzing={analyzing} onAnalyze={analyzeRisk} onBack={() => navigate('transactions')} onAskAssistant={() => navigate('assistant')} />}
          {page === 'transaction-details' && !selectedTransaction && <EmptyState icon={CreditCard} title="Choose a transaction" detail="Open a transaction from the ledger to view its details." />}
          {page === 'disputes' && <DisputeCenter disputes={disputes} transactions={transactions} onResolved={refreshData} initialDispute={selectedDispute} />}
          {page === 'risk' && <><PageHeading eyebrow="MODEL-ASSISTED REVIEW" title="Risk analysis" detail="Review existing risk indicators, then analyze a transaction using the trained model." action={<button className="button button-secondary" onClick={() => navigate('transactions')}><Search size={16} /> Find a transaction</button>} /><div className="risk-callout"><div className="risk-callout-icon"><ShieldAlert size={19} /></div><div><strong>Risk indicators are signals, not verdicts.</strong><p>Model results support human review and should be considered alongside verified transaction records.</p></div></div><section className="panel table-panel"><div className="panel-heading"><div><p className="eyebrow">FLAGGED FOR REVIEW</p><h2>Elevated indicators</h2></div><Badge tone="warning" dot>{transactions.filter((item) => ['high', 'elevated', 'critical', 'medium'].includes(String(item.fraud_risk_label).toLowerCase())).length} records</Badge></div><TransactionTable transactions={[...transactions].reverse()} onSelect={openTransaction} showSearch riskOnly /></section></>}
          {page === 'assistant' && <><PageHeading eyebrow="MERCHANT GUIDANCE" title="AI Merchant Assistant" detail="Ask about application transactions, risk results, and safe dispute review steps." /><AssistantChat transactions={transactions} initialTransactionId={selectedTransaction?.transaction_id} onSelectTransaction={openTransaction} /></>}
          <footer className="content-footer"><span>AI Merchant Assistant <i /> Synthetic data only</span><span>Merchant review required for all dispute actions</span></footer>
        </div>
      </main>
    </div>
  );
}
