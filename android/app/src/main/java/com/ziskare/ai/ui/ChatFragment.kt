package com.ziskare.ai.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.ImageButton
import android.widget.TextView
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.ziskare.ai.R
import com.ziskare.ai.db.entity.Session
import com.ziskare.ai.ui.adapter.MessageAdapter
import com.ziskare.ai.viewmodel.ChatUiState
import com.ziskare.ai.viewmodel.ChatViewModel
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.launch

class ChatFragment : Fragment() {

    companion object {
        private const val ARG_ID = "session_id"
        private const val ARG_TITLE = "session_title"

        fun newInstance(session: Session) = ChatFragment().apply {
            arguments = Bundle().apply {
                putString(ARG_ID, session.id)
                putString(ARG_TITLE, session.title)
            }
        }
    }

    private val vm: ChatViewModel by activityViewModels()
    private val sessionId by lazy { requireArguments().getString(ARG_ID)!! }

    override fun onCreateView(inf: LayoutInflater, c: ViewGroup?, s: Bundle?): View =
        inf.inflate(R.layout.fragment_chat, c, false)

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        val rv = view.findViewById<RecyclerView>(R.id.rvMessages)
        val et = view.findViewById<EditText>(R.id.etInput)
        val btnSend = view.findViewById<ImageButton>(R.id.btnSend)
        val tvOffline = view.findViewById<TextView>(R.id.tvOfflineBanner)
        val tvLoading = view.findViewById<TextView>(R.id.tvLoading)

        val adapter = MessageAdapter()
        rv.layoutManager = LinearLayoutManager(requireContext()).apply { stackFromEnd = true }
        rv.adapter = adapter

        // Observe messages from Room - works offline
        viewLifecycleOwner.lifecycleScope.launch {
            vm.getMessages(sessionId).collectLatest { msgs ->
                adapter.submitList(msgs)
                if (msgs.isNotEmpty()) rv.scrollToPosition(msgs.size - 1)
            }
        }

        // Observe UI state (loading / offline / error)
        viewLifecycleOwner.lifecycleScope.launch {
            vm.uiState.collectLatest { state ->
                tvLoading.visibility = if (state is ChatUiState.Loading) View.VISIBLE else View.GONE
                when (state) {
                    is ChatUiState.Offline -> {
                        tvOffline.visibility = View.VISIBLE
                        Toast.makeText(requireContext(), "Server offline - history loaded from device", Toast.LENGTH_SHORT).show()
                    }
                    is ChatUiState.Err -> {
                        tvOffline.visibility = View.GONE
                        Toast.makeText(requireContext(), state.msg, Toast.LENGTH_LONG).show()
                    }
                    else -> tvOffline.visibility = View.GONE
                }
            }
        }

        btnSend.setOnClickListener {
            val text = et.text.toString().trim()
            if (text.isBlank()) return@setOnClickListener
            et.setText("")
            vm.sendMessage(sessionId, text)
        }
    }
}
